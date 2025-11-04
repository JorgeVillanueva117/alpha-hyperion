"""
core_system.py
Sistema principal Alpha Hyperion v5.3 - Modular y Ultrarrápido
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

class AlphaHyperionSystem:
    """Sistema completo de routing inteligente con meta-supervisión"""
    
    def __init__(self, experts: Optional[List[Expert]] = None):
        # Inicializar expertos
        self.experts_list = experts or ExpertFactory.create_default_experts()
        self.experts = {exp.id: exp for exp in self.experts_list}
        
        # Componentes del sistema
        self.classifier = FastPatternClassifier()
        self.monte_carlo = MonteCarloEngine()
        self.router = IntelligentRouter(self.experts)
        self.meta_agent = MetaAgent("primary_supervisor")
        
        # Estadísticas
        self.routing_history = deque(maxlen=500)
        self.total_queries = 0
        self.successful_routings = 0
        
        # Mapeo de dominios
        self.domain_mapping = ExpertFactory.get_domain_mapping()
        
        print(f"✓ Alpha Hyperion v5.3 inicializado")
        print(f"  - Expertos: {len(self.experts)}")
        print(f"  - Clasificador rápido: FastPatternClassifier")
        print(f"  - Motor MC: Optimizado con caché")
        print(f"  - Meta-agente: {self.meta_agent.name}")
    
    def route_query(self, query: str) -> Dict:
        """
        Ruta una consulta al experto óptimo
        
        Returns:
            Dict con: expert, performance, routing_time, query_time, total_time
        """
        start_total = time.perf_counter()
        
        # FASE 1: Clasificación ultrarrápida
        start_routing = time.perf_counter()
        domains, complexity, reasoning = self.classifier.classify_fast(query)
        
        # Crear tarea
        task = Task(
            id=f"query_{int(time.time() * 1000)}",
            domain_breadth=complexity,
            interdependency=complexity * (1.1 if len(domains) > 1 else 1.0),
            task_scope=complexity * 1.05,
            required_domains=domains,
            query=query
        )
        
        # FASE 2: Selección de expertos
        candidates = self._get_relevant_experts(task)
        selected_experts_ids = self.router.select_experts(candidates, task)
        
        # Objetos de expertos
        selected_experts = [self.experts[exp_id] for exp_id in selected_experts_ids]
        
        # FASE 3: Predicción Monte Carlo (rápida)
        mc_results = self.monte_carlo.simulate_collaboration(selected_experts, task)
        
        routing_time = (time.perf_counter() - start_routing) * 1000
        
        # Calcular métricas
        routing_type = 'MULTI' if len(selected_experts) > 1 else 'SINGLE'
        routing_reason = self._generate_routing_reason(task, selected_experts, complexity)
        
        # Verificar acierto
        self.total_queries += 1
        if self._is_routing_successful(task, selected_experts_ids):
            self.successful_routings += 1
        
        # Actualizar expertos y memoria
        for expert in selected_experts:
            expert.update_performance(mc_results['mean_performance'], task.complexity)
            self.router.update_performance_memory(expert.id, task, mc_results['mean_performance'])
        
        # Meta-agente observa
        self.meta_agent.observe(selected_experts, task, mc_results)
        
        # FASE 4: Consulta a Ollama (simulada - tiempo real en producción)
        start_query = time.perf_counter()
        # En producción, aquí iría: ollama_client.query_model(selected_experts[0].id, query)
        # Para este demo, simulamos tiempo de consulta realista
        time.sleep(0.001)  # 1ms simulado (Ollama real ~50-500ms)
        query_time = (time.perf_counter() - start_query) * 1000
        
        total_time = (time.perf_counter() - start_total) * 1000
        
        # Resultado
        result = {
            'query': query,
            'experts': selected_experts_ids,
            'primary_expert': selected_experts[0].id,
            'domains': domains,
            'complexity': complexity,
            'type': routing_type,
            'reasoning': reasoning,
            'routing_reason': routing_reason,
            
            # Métricas de rendimiento
            'expected_performance': mc_results['mean_performance'],
            'success_probability': mc_results['success_probability'],
            'synergy': mc_results.get('synergy', 1.0),
            
            # Tiempos (crítico!)
            'routing_time_ms': routing_time,
            'query_time_ms': query_time,
            'total_time_ms': total_time,
            
            # Estadísticas
            'mc_simulations': mc_results['simulation_count'],
            'success_rate': self.get_success_rate()
        }
        
        self.routing_history.append(result)
        return result
    
    def _get_relevant_experts(self, task: Task) -> List[str]:
        """Obtiene expertos relevantes para la tarea"""
        relevant = []
        
        # Mapeo estricto de dominios
        for domain in task.required_domains:
            expert_id = self.domain_mapping.get(domain)
            if expert_id and expert_id not in relevant:
                relevant.append(expert_id)
        
        # Ordenar por score si hay múltiples
        if len(relevant) > 1:
            scored = []
            for exp_id in relevant:
                expert = self.experts[exp_id]
                score = (expert.success_rate * expert.specialization_score * 
                        expert.availability * (1.0 - expert.fatigue / expert.max_load_capacity))
                scored.append((exp_id, score))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            relevant = [exp_id for exp_id, _ in scored]
        
        # Fallback
        if not relevant:
            relevant = [list(self.experts.keys())[0]]
        
        return relevant
    
    def _generate_routing_reason(self, task: Task, experts: List[Expert], 
                                 complexity: float) -> str:
        """Genera explicación del routing"""
        num_domains = len(task.required_domains)
        
        if num_domains == 1:
            return f"Dominio único ({task.required_domains[0]}) - Experto especializado óptimo"
        elif num_domains >= 2 and complexity > 0.40:
            return (f"Tarea multi-dominio ({num_domains} dominios, "
                   f"complejidad: {complexity:.2f}) - Colaboración necesaria")
        else:
            return f"Multi-dominio de baja complejidad ({complexity:.2f}) - Experto principal suficiente"
    
    def _is_routing_successful(self, task: Task, selected_experts: List[str]) -> bool:
        """Verifica si el routing fue acertado"""
        if not task.required_domains or not selected_experts:
            return False
        
        primary_expert = self.experts[selected_experts[0]]
        return primary_expert.domain in task.required_domains
    
    def get_success_rate(self) -> float:
        """Tasa de acierto actual"""
        if self.total_queries == 0:
            return 100.0
        return (self.successful_routings / self.total_queries) * 100
    
    def get_statistics(self) -> Dict:
        """Estadísticas completas del sistema"""
        if not self.routing_history:
            return {'total_queries': 0}
        
        recent = list(self.routing_history)[-50:]
        
        avg_routing_time = np.mean([r['routing_time_ms'] for r in recent])
        avg_query_time = np.mean([r['query_time_ms'] for r in recent])
        avg_total_time = np.mean([r['total_time_ms'] for r in recent])
        avg_performance = np.mean([r['expected_performance'] for r in recent])
        
        multi_expert_count = sum(1 for r in recent if r['type'] == 'MULTI')
        
        cache_stats = self.classifier.get_cache_stats()
        meta_stats = self.meta_agent.get_statistics()
        balance_status = self.router.get_balance_status()
        
        return {
            'total_queries': self.total_queries,
            'successful_routings': self.successful_routings,
            'success_rate': self.get_success_rate(),
            
            'avg_routing_time_ms': avg_routing_time,
            'avg_query_time_ms': avg_query_time,
            'avg_total_time_ms': avg_total_time,
            
            'avg_performance': avg_performance,
            'multi_expert_rate': multi_expert_count / len(recent) * 100 if recent else 0,
            
            'cache_stats': cache_stats,
            'meta_agent_stats': meta_stats,
            'balance_status': balance_status
        }
    
    def print_statistics(self):
        """Imprime estadísticas formateadas"""
        stats = self.get_statistics()
        
        print("\n" + "="*80)
        print("📊 ESTADÍSTICAS DEL SISTEMA")
        print("="*80)
        
        print(f"\n🎯 Precisión:")
        print(f"  - Total consultas: {stats['total_queries']}")
        print(f"  - Routings acertados: {stats['successful_routings']}")
        print(f"  - Tasa de acierto: {stats['success_rate']:.2f}%")
        
        if stats['total_queries'] > 0:
            print(f"\n⚡ Velocidad:")
            print(f"  - Routing promedio: {stats['avg_routing_time_ms']:.2f} ms")
            print(f"  - Consulta promedio: {stats['avg_query_time_ms']:.2f} ms")
            print(f"  - Total promedio: {stats['avg_total_time_ms']:.2f} ms")
            
            print(f"\n📈 Rendimiento:")
            print(f"  - Performance esperado: {stats['avg_performance']:.1%}")
            print(f"  - Colaboraciones: {stats['multi_expert_rate']:.1f}%")
            
            cache = stats['cache_stats']
            print(f"\n💾 Caché:")
            print(f"  - Tamaño: {cache['cache_size']}")
            print(f"  - Hit rate: {cache['hit_rate']:.1%}")
            
            meta = stats['meta_agent_stats']
            print(f"\n🤖 Meta-agente:")
            print(f"  - Observaciones: {meta['observations']}")
            print(f"  - Intervenciones: {meta['interventions']}")
            if 'avg_performance_recent' in meta:
                print(f"  - Performance reciente: {meta['avg_performance_recent']:.1%}")
        
        print("="*80)