"""
monte_carlo_engine.py
Motor de simulación Monte Carlo para Alpha Hyperion v5.3
"""

import numpy as np
from typing import List, Dict
from expert_models import Expert, Task, SYNERGY_MATRIX_BASE

class MonteCarloEngine:
    def __init__(self, num_simulations: int = 60):
        self.num_simulations = num_simulations
        self.rng = np.random.default_rng()

    def simulate_collaboration(self, experts: List[Expert], task: Task) -> Dict:
        if not experts:
            return {"mean_performance": 0.0, "success_probability": 0.0, "simulation_count": 0}

        n = len(experts)
        performances = np.zeros((self.num_simulations, n))
        
        for i, expert in enumerate(experts):
            base_perf = expert.success_rate * expert.specialization_score
            noise = self.rng.normal(0, 0.05, self.num_simulations)
            load_factor = 1.0 - (expert.fatigue / expert.max_load_capacity)
            complexity_penalty = 1.0 - (task.complexity * 0.3)
            
            performances[:, i] = base_perf * load_factor * complexity_penalty + noise
            performances[:, i] = np.clip(performances[:, i], 0.1, 1.0)

        # Aplicar sinergia
        if n > 1:
            synergy_factors = self._compute_synergy(experts)
            for i in range(n):
                for j in range(n):
                    if i != j:
                        performances[:, i] *= (1 + synergy_factors[i, j] * 0.15)

        collab_perf = np.mean(performances, axis=1)
        mean_perf = float(np.mean(collab_perf))
        success_prob = float(np.mean(collab_perf >= 0.75))
        
        return {
            "mean_performance": mean_perf,
            "success_probability": success_prob,
            "synergy": float(np.mean(synergy_factors)) if n > 1 else 1.0,
            "simulation_count": self.num_simulations
        }

    def _compute_synergy(self, experts: List[Expert]) -> np.ndarray:
        indices = {exp.domain: i for i, exp in enumerate(experts)}
        synergy = np.ones((len(experts), len(experts)))
        
        for i, exp1 in enumerate(experts):
            for j, exp2 in enumerate(experts):
                if i != j:
                    d1, d2 = exp1.domain, exp2.domain
                    idx1 = ["mathematics", "programming", "language"].index(d1)
                    idx2 = ["mathematics", "programming", "language"].index(d2)
                    synergy[i, j] = SYNERGY_MATRIX_BASE[idx1, idx2]
        
        return synergy