"""
intelligent_router.py
Router inteligente con balance de carga y memoria de rendimiento
"""

import numpy as np
from typing import List, Dict
from collections import deque, defaultdict
from expert_models import Expert, Task

class IntelligentRouter:
    """Router con balance adaptativo y aprendizaje"""
    
    def __init__(self, experts: Dict[str, Expert]):
        self.experts = experts
        self.performance_memory = defaultdict(lambda: deque(maxlen=50))
        self.task_history = deque(maxlen=200)
        self.expert_assignments = defaultdict(int)
        
    def select_experts(self, candidates: List[str], task: Task) -> List[str]:
        """
        Selecciona expertos óptimos para una tarea
        
        Reglas:
        - 1 dominio = 1 experto
        - Multi-dominio complejo = colaboración
        - Balance de carga considerado
        """
        if not candidates:
            return [list(self.experts.keys())[0]]
        
        num_domains = len(task.required_domains)
        complexity = task.complexity
        
        # REGLA 1: Un dominio = Un experto
        if num_domains == 1:
            return [candidates[0]]
        
        # REGLA 2: Multi-dominio
        if num_domains >= 2:
            # Complejidad alta = colaboración
            if complexity > 0.40:
                # Seleccionar top 2 expertos balanceados
                scored_candidates = []
                for exp_id in candidates[:3]:
                    expert = self.experts[exp_id]
                    score = self._calculate_expert_score(expert, task)
                    scored_candidates.append((exp_id, score))
                
                scored_candidates.sort(key=lambda x: x[1], reverse=True)
                selected = [scored_candidates[0][0]]
                
                # Agregar segundo experto si mejora balance
                if len(scored_candidates) > 1:
                    first_domain = self.experts[selected[0]].domain
                    for exp_id, _ in scored_candidates[1:]:
                        if self.experts[exp_id].domain != first_domain:
                            selected.append(exp_id)
                            break
                
                return selected
            else:
                # Baja complejidad = experto principal
                return [candidates[0]]
        
        return [candidates[0]]
    
    def _calculate_expert_score(self, expert: Expert, task: Task) -> float:
        """Calcula score de experto para una tarea"""
        # Componentes del score
        performance_score = expert.success_rate * expert.specialization_score
        availability_score = expert.availability * (1.0 - expert.fatigue / expert.max_load_capacity)
        
        # Bonus por dominio relevante
        domain_bonus = 1.2 if expert.domain in task.required_domains else 1.0
        
        # Penalización por carga alta
        load_penalty = 1.0 / (1.0 + expert.load * 0.15)
        
        # Historial de rendimiento reciente
        recent_perf = self._get_recent_performance(expert.id, task.required_domains)
        history_bonus = 1.0 + (recent_perf - 0.75) * 0.5 if recent_perf > 0 else 1.0
        
        total_score = (performance_score * availability_score * 
                      domain_bonus * load_penalty * history_bonus)
        
        return total_score
    
    def _get_recent_performance(self, expert_id: str, domains: List[str]) -> float:
        """Obtiene rendimiento reciente del experto en dominios similares"""
        key = f"{expert_id}_{'_'.join(sorted(domains))}"
        history = self.performance_memory.get(key, [])
        
        if not history:
            return 0.0
        
        # Peso mayor a rendimientos recientes
        weights = np.linspace(0.5, 1.0, len(history))
        weighted_perf = np.average(list(history), weights=weights)
        return weighted_perf
    
    def update_performance_memory(self, expert_id: str, task: Task, performance: float):
        """Actualiza memoria de rendimiento"""
        key = f"{expert_id}_{'_'.join(sorted(task.required_domains))}"
        self.performance_memory[key].append(performance)
        
        self.task_history.append({
            'expert': expert_id,
            'domains': task.required_domains,
            'performance': performance,
            'complexity': task.complexity
        })
        
        self.expert_assignments[expert_id] += 1
    
    def get_balance_status(self) -> Dict:
        """Obtiene estado de balance del sistema"""
        if not self.expert_assignments:
            return {'balanced': True, 'distribution': {}}
        
        total_assignments = sum(self.expert_assignments.values())
        distribution = {
            exp_id: count / total_assignments 
            for exp_id, count in self.expert_assignments.items()
        }
        
        # Verificar balance (diferencia máxima < 20%)
        values = list(distribution.values())
        is_balanced = (max(values) - min(values)) < 0.20 if values else True
        
        return {
            'balanced': is_balanced,
            'distribution': distribution,
            'total_assignments': total_assignments
        }