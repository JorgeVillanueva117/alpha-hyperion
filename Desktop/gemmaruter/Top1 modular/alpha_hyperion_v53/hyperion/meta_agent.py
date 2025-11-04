"""
meta_agent.py
Meta-agente que supervisa, detecta conflictos y optimiza el sistema
"""

import time
import numpy as np
from typing import List, Dict, Optional
from collections import deque
from expert_models import Expert, Task

class MetaAgent:
    """Supervisor inteligente del sistema de expertos"""
    
    def __init__(self, name: str = "meta_supervisor", memory_size: int = 500):
        self.name = name
        self.observations = deque(maxlen=memory_size)
        self.reputation = {}  # Reputación por experto
        self.intervention_history = deque(maxlen=200)
        
        self.intervention_count = 0
        self.last_intervention_time = 0
        self.min_intervention_interval = 5  # segundos
        
        # Thresholds
        self.conflict_threshold_std = 0.06
        self.low_synergy_threshold = 0.98
        self.low_performance_threshold = 0.72
    
    def observe(self, experts: List[Expert], task: Task, mc_results: Dict, 
                individual_contributions: Optional[List[float]] = None):
        """Observa resultado de ejecución y actualiza métricas"""
        obs = {
            'timestamp': time.time(),
            'task_id': task.id,
            'domains': task.required_domains,
            'complexity': task.complexity,
            'mean_perf': mc_results.get('mean_performance', 0.0),
            'std_perf': mc_results.get('std_performance', 0.0),
            'synergy': mc_results.get('synergy', 1.0),
            'experts': [e.id for e in experts],
            'individual_contributions': individual_contributions
        }
        
        self.observations.append(obs)
        
        # Actualizar reputación
        for expert in experts:
            old_rep = self.reputation.get(expert.id, 0.5)
            perf_delta = (obs['mean_perf'] - 0.7) * 0.2
            self.reputation[expert.id] = np.clip(old_rep + perf_delta, 0.0, 1.0)
        
        # Detectar y resolver conflictos
        if self._detect_conflict(obs):
            self._intervene(experts, task, mc_results, obs)
        else:
            # Aprendizaje pasivo de estrategias exitosas
            if obs['mean_perf'] > 0.82 and obs['synergy'] > 1.01:
                self.intervention_history.append({
                    'type': 'success_pattern',
                    'domains': task.required_domains,
                    'performance': obs['mean_perf'],
                    'synergy': obs['synergy'],
                    'time': time.time()
                })
    
    def _detect_conflict(self, obs: Dict) -> bool:
        """Detecta conflictos o bajo rendimiento"""
        # Conflicto por alta varianza
        if obs['std_perf'] > self.conflict_threshold_std:
            return True
        
        # Conflicto por baja sinergia
        if obs['synergy'] < self.low_synergy_threshold and len(obs['experts']) > 1:
            return True
        
        # Bajo rendimiento general
        if obs['mean_perf'] < self.low_performance_threshold:
            return True
        
        # Conflicto por contribuciones desbalanceadas
        if obs['individual_contributions']:
            contrib_std = float(np.std(obs['individual_contributions']))
            if contrib_std > self.conflict_threshold_std:
                return True
        
        return False
    
    def _intervene(self, experts: List[Expert], task: Task, 
                   mc_results: Dict, obs: Dict):
        """Interviene para resolver conflictos"""
        now = time.time()
        
        # Cooldown entre intervenciones
        if now - self.last_intervention_time < self.min_intervention_interval:
            return
        
        self.last_intervention_time = now
        self.intervention_count += 1
        
        interventions = []
        synergy = mc_results.get('synergy', 1.0)
        mean_perf = mc_results.get('mean_performance', 0.7)
        
        # INTERVENCIÓN 1: Ajustar historial de colaboración si sinergia baja
        if synergy < 1.0 and len(experts) > 1:
            for i, e1 in enumerate(experts):
                for e2 in experts[i+1:]:
                    current_collab = e1.collaboration_history.get(e2.id, 1.0)
                    new_collab = np.clip(current_collab - 0.03, 0.70, 1.12)
                    
                    e1.collaboration_history[e2.id] = new_collab
                    e2.collaboration_history[e1.id] = new_collab
                    
                    interventions.append(
                        f"Ajustada colaboración {e1.id[:8]}<->{e2.id[:8]}: {new_collab:.3f}"
                    )
        
        # INTERVENCIÓN 2: Boost a expertos con alta reputación
        if mean_perf < 0.78:
            for expert in experts:
                rep = self.reputation.get(expert.id, 0.5)
                if rep > 0.6:
                    old_spec = expert.specialization_score
                    expert.specialization_score = np.clip(old_spec + 0.05, 0.7, 2.0)
                    interventions.append(
                        f"Aumentada especialización {expert.id[:8]}: "
                        f"{old_spec:.2f}→{expert.specialization_score:.2f}"
                    )
        
        # INTERVENCIÓN 3: Redistribución si varianza alta
        if obs['std_perf'] > 0.10:
            # Sugerir priorizar experto con menor fatiga
            best_expert = min(experts, key=lambda x: (x.fatigue, -x.availability))
            best_expert.availability = min(1.0, best_expert.availability + 0.03)
            interventions.append(
                f"Priorizado {best_expert.id[:8]} (fatiga: {best_expert.fatigue:.2f})"
            )
        
        # Registrar intervención
        if interventions:
            self.intervention_history.append({
                'type': 'conflict_resolution',
                'task_id': task.id,
                'interventions': interventions,
                'performance': mean_perf,
                'synergy': synergy,
                'time': now
            })
    
    def get_summary(self, last_n: int = 10) -> Dict:
        """Resumen de intervenciones recientes"""
        recent = list(self.intervention_history)[-last_n:]
        
        return {
            'meta_name': self.name,
            'total_interventions': self.intervention_count,
            'recent_interventions': recent,
            'reputation_snapshot': dict(self.reputation)
        }
    
    def get_statistics(self) -> Dict:
        """Estadísticas del meta-agente"""
        if not self.observations:
            return {'observations': 0}
        
        recent_obs = list(self.observations)[-50:]
        
        avg_perf = np.mean([obs['mean_perf'] for obs in recent_obs])
        avg_synergy = np.mean([obs['synergy'] for obs in recent_obs if obs['synergy'] > 1.0])
        
        conflict_count = sum(1 for obs in recent_obs 
                            if obs['std_perf'] > self.conflict_threshold_std or 
                               obs['synergy'] < self.low_synergy_threshold)
        
        return {
            'observations': len(self.observations),
            'interventions': self.intervention_count,
            'avg_performance_recent': avg_perf,
            'avg_synergy_recent': avg_synergy if avg_synergy > 0 else 1.0,
            'conflict_rate': conflict_count / len(recent_obs) if recent_obs else 0,
            'reputation_scores': dict(self.reputation)
        }