"""
core_system.py
Sistema principal Alpha Hyperion v5.3 - Con Ollama REAL + Carga de modelos
"""

import time
import numpy as np
from typing import List, Dict, Optional
from collections import deque

from expert_models import Expert, Task, ExpertFactory
from fast_classifier import FastPatternClassifier
from monte_carlo_engine import MonteCarloEngine
from intelligent_router import IntelligentRouter
from meta_agent import MetaAgent

# IMPORT OLLAMA
try:
    import ollama
    OLLAMA_AVAILABLE = True
    print("Ollama detectado")
except ImportError:
    OLLAMA_AVAILABLE = False
    print("ollama no instalado → pip install ollama")

class AlphaHyperionSystem:
    def __init__(self, experts: Optional[List[Expert]] = None):
        self.experts_list = experts or ExpertFactory.create_default_experts()
        self.experts = {exp.id: exp for exp in self.experts_list}
        
        self.classifier = FastPatternClassifier()
        self.monte_carlo = MonteCarloEngine()
        self.router = IntelligentRouter(self.experts)
        self.meta_agent = MetaAgent("primary_supervisor")
        
        self.routing_history = deque(maxlen=500)
        self.total_queries = 0
        self.successful_routings = 0
        self.domain_mapping = ExpertFactory.get_domain_mapping()
        
        # CARGA MODELOS AL INICIO
        self._preload_models()
        
        print(f"Alpha Hyperion v5.3 inicializado")
        print(f"  - Expertos: {len(self.experts)}")
        print(f"  - Modelos cargados: {', '.join(self.experts.keys())}")
        print(f"  - Ollama: {'Conectado' if OLLAMA_AVAILABLE else 'No disponible'}")
    
    def _preload_models(self):
        """Carga todos los modelos al inicio"""
        if not OLLAMA_AVAILABLE:
            return
        
        print("Cargando modelos en memoria...")
        for expert_id in self.experts.keys():
            try:
                print(f"  Cargando {expert_id}...", end="")
                ollama.show(expert_id)  # Fuerza carga en RAM
                print("OK")
            except Exception as e:
                print(f"FALLÓ → {e}")
        print("Todos los modelos listos en RAM")

    def route_query(self, query: str) -> Dict:
        start_total = time.perf_counter()
        start_routing = time.perf_counter()
        
        domains, complexity, reasoning = self.classifier.classify_fast(query)
        task = Task(
            id=f"query_{int(time.time() * 1000)}",
            domain_breadth=complexity,
            interdependency=complexity * (1.1 if len(domains) > 1 else 1.0),
            task_scope=complexity * 1.05,
            required_domains=domains,
            query=query
        )
        
        candidates = self._get_relevant_experts(task)
        selected_experts_ids = self.router.select_experts(candidates, task)
        selected_experts = [self.experts[exp_id] for exp_id in selected_experts_ids]
        
        mc_results = self.monte_carlo.simulate_collaboration(selected_experts, task)
        routing_time = (time.perf_counter() - start_routing) * 1000
        
        routing_type = 'MULTI' if len(selected_experts) > 1 else 'SINGLE'
        routing_reason = self._generate_routing_reason(task, selected_experts, complexity)
        
        self.total_queries += 1
        if self._is_routing_successful(task, selected_experts_ids):
            self.successful_routings += 1
        
        for expert in selected_experts:
            expert.update_performance(mc_results['mean_performance'], task.complexity)
            self.router.update_performance_memory(expert.id, task, mc_results['mean_performance'])
        
        self.meta_agent.observe(selected_experts, task, mc_results)
        
        # CONSULTA A OLLAMA (REAL) - CORREGIDO
        ollama_result = self._query_ollama(selected_experts[0].id, query)
        response_text = ollama_result['response']
        query_time_ms = ollama_result['query_time']
        
        total_time = (time.perf_counter() - start_total) * 1000
        
        result = {
            'query': query,
            'experts': selected_experts_ids,
            'primary_expert': selected_experts[0].id,
            'domains': domains,
            'complexity': complexity,
            'type': routing_type,
            'reasoning': reasoning,
            'routing_reason': routing_reason,
            'expected_performance': mc_results['mean_performance'],
            'success_probability': mc_results['success_probability'],
            'synergy': mc_results.get('synergy', 1.0),
            'routing_time_ms': routing_time,
            'query_time_ms': query_time_ms,
            'total_time_ms': total_time,
            'mc_simulations': mc_results['simulation_count'],
            'success_rate': self.get_success_rate(),
            'response': response_text.strip()
        }
        
        self.routing_history.append(result)
        return result

    def _query_ollama(self, model_id: str, query: str) -> Dict:
        """Consulta a Ollama con manejo seguro"""
        if not OLLAMA_AVAILABLE:
            time.sleep(0.001)
            return {'response': f"[Simulado: {query}]", 'query_time': 1.0}
        
        start = time.perf_counter()
        try:
            response = ollama.chat(
                model=model_id,
                messages=[{'role': 'user', 'content': query}]
            )
            content = response.get('message', {}).get('content', '')
            duration = response.get('total_duration', 0) / 1_000_000
            return {'response': content, 'query_time': duration}
        except Exception as e:
            error_msg = f"[Ollama Error: {e}]"
            return {'response': error_msg, 'query_time': (time.perf_counter() - start) * 1000}

    def _get_relevant_experts(self, task: Task) -> List[str]:
        relevant = []
        for domain in task.required_domains:
            expert_id = self.domain_mapping.get(domain)
            if expert_id and expert_id not in relevant:
                relevant.append(expert_id)
        if not relevant:
            relevant = [list(self.experts.keys())[0]]
        return relevant

    def _generate_routing_reason(self, task: Task, experts: List[Expert], complexity: float) -> str:
        num = len(task.required_domains)
        if num == 1:
            return f"Dominio único ({task.required_domains[0]}) - Experto especializado óptimo"
        elif num >= 2 and complexity > 0.40:
            return f"Tarea multi-dominio ({num} dominios, complejidad: {complexity:.2f})"
        else:
            return f"Multi-dominio de baja complejidad ({complexity:.2f})"

    def _is_routing_successful(self, task: Task, selected_experts: List[str]) -> bool:
        if not task.required_domains or not selected_experts:
            return False
        primary = self.experts[selected_experts[0]]
        return primary.domain in task.required_domains

    def get_success_rate(self) -> float:
        return 100.0 if self.total_queries == 0 else (self.successful_routings / self.total_queries) * 100

    def get_statistics(self) -> Dict:
        if not self.routing_history:
            return {'total_queries': 0}
        recent = list(self.routing_history)[-50:]
        return {
            'total_queries': self.total_queries,
            'successful_routings': self.successful_routings,
            'success_rate': self.get_success_rate(),
            'avg_routing_time_ms': np.mean([r['routing_time_ms'] for r in recent]),
            'avg_query_time_ms': np.mean([r['query_time_ms'] for r in recent]),
            'avg_total_time_ms': np.mean([r['total_time_ms'] for r in recent]),
            'avg_performance': np.mean([r['expected_performance'] for r in recent]),
            'multi_expert_rate': sum(1 for r in recent if r['type'] == 'MULTI') / len(recent) * 100,
            'cache_stats': self.classifier.get_cache_stats(),
            'meta_agent_stats': self.meta_agent.get_statistics(),
            'balance_status': self.router.get_balance_status(),
            'ollama_available': OLLAMA_AVAILABLE
        }

    def print_statistics(self):
        stats = self.get_statistics()
        print("\n" + "="*80)
        print("ESTADÍSTICAS DEL SISTEMA")
        print("="*80)
        print(f"Total consultas: {stats['total_queries']}")
        print(f"Tasa de acierto: {stats['success_rate']:.2f}%")
        if stats['total_queries'] > 0:
            print(f"Routing promedio: {stats['avg_routing_time_ms']:.2f} ms")
            print(f"Consulta promedio: {stats['avg_query_time_ms']:.2f} ms")
            print(f"Total promedio: {stats['avg_total_time_ms']:.2f} ms")
            print(f"Performance: {stats['avg_performance']:.1%}")
        print(f"Ollama: {'Conectado' if OLLAMA_AVAILABLE else 'No disponible'}")
        print("="*80)
