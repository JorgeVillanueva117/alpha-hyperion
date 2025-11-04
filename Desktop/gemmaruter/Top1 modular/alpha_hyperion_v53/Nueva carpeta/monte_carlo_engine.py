"""
monte_carlo_engine.py
Motor Monte Carlo optimizado para predicción de rendimiento
"""

import numpy as np
from typing import List, Dict
from expert_models import Expert, Task, SYNERGY_MATRIX_BASE, BENCHMARK_DATASETS

class MonteCarloEngine:
    """Motor Monte Carlo con sampling adaptativo"""
    
    def __init__(self, min_simulations: int = 60, max_simulations: int = 150):
        self.min_simulations = min_simulations
        self.max_simulations = max_simulations
        self.simulation_cache = {}
        
    def simulate_collaboration(self, experts: List[Expert], task: Task) -> Dict:
        """
        Simula colaboración de expertos
        Returns: dict con métricas de rendimiento predichas
        """
        # Determinar número óptimo de simulaciones
        n_sims = self._calculate_optimal_simulations(task, experts)
        
        # Cache check (basado en expertos + complejidad)
        cache_key = self._generate_cache_key(experts, task)
        if cache_key in self.simulation_cache:
            return self.simulation_cache[cache_key]
        
        # Simulación
        if len(experts) == 1:
            result = self._simulate_single_expert(experts[0], task, n_sims)
        else:
            result = self._simulate_multi_expert(experts, task, n_sims)
        
        # Cache result
        if len(self.simulation_cache) < 500:
            self.simulation_cache[cache_key] = result
        
        return result
    
    def _calculate_optimal_simulations(self, task: Task, experts: List[Expert]) -> int:
        """Calcula número óptimo de simulaciones basado en complejidad"""
        base = 80
        complexity_factor = min(1.4, task.complexity / 0.7)
        team_factor = 1.0 + (len(experts) - 1) * 0.08
        optimal = int(base * complexity_factor * team_factor)
        return max(self.min_simulations, min(self.max_simulations, optimal))
    
    def _generate_cache_key(self, experts: List[Expert], task: Task) -> str:
        """Genera clave de caché única"""
        expert_ids = "_".join(sorted([e.id for e in experts]))
        complexity_bucket = round(task.complexity, 2)
        domains = "_".join(sorted(task.required_domains))
        return f"{expert_ids}_{domains}_{complexity_bucket}"
    
    def _simulate_single_expert(self, expert: Expert, task: Task, n_sims: int) -> Dict:
        """Simula rendimiento de un solo experto"""
        results = []
        
        # Buscar benchmark esperado
        expected_perf = expert.success_rate
        min_diff = float('inf')
        
        for dataset in BENCHMARK_DATASETS.values():
            for benchmark in dataset:
                if expert.domain in benchmark['domains']:
                    diff = abs(task.complexity - benchmark['complexity'])
                    if diff < min_diff:
                        min_diff = diff
                        expected_perf = benchmark['expected_performance']
        
        # Ejecutar simulaciones
        for _ in range(n_sims):
            base_perf = expected_perf
            
            # Factores de ajuste
            fatigue_impact = max(0.88, 1.0 - expert.fatigue / 20.0)
            load_impact = max(0.90, 1.0 / (1.0 + expert.load * 0.25))
            domain_bonus = 1.08 if expert.domain in task.required_domains else 1.0
            specialization_bonus = 1.0 + (expert.specialization_score - 1.0) * 0.15
            
            # Ruido estocástico
            noise = np.random.normal(0, 0.06)
            
            performance = (base_perf * fatigue_impact * load_impact * 
                          domain_bonus * specialization_bonus + noise)
            results.append(np.clip(performance, 0.45, 0.92))
        
        return {
            'mean_performance': np.mean(results),
            'std_performance': np.std(results),
            'confidence_interval': np.percentile(results, [10, 90]),
            'success_probability': np.sum(np.array(results) > 0.70) / n_sims,
            'simulation_count': len(results),
            'synergy': 1.0
        }
    
    def _simulate_multi_expert(self, experts: List[Expert], task: Task, n_sims: int) -> Dict:
        """Simula colaboración multi-experto"""
        results = []
        
        # Calcular sinergia esperada
        synergy = self._calculate_synergy(experts, task)
        
        # Buscar benchmark para equipo
        expected_perf = np.mean([e.success_rate for e in experts])
        min_diff = float('inf')
        
        for dataset in BENCHMARK_DATASETS.values():
            for benchmark in dataset:
                team_domains = set([e.domain for e in experts])
                if set(benchmark['domains']).issubset(team_domains):
                    diff = abs(task.complexity - benchmark['complexity'])
                    if diff < min_diff:
                        min_diff = diff
                        expected_perf = benchmark['expected_performance']
        
        # Simulaciones
        for _ in range(n_sims):
            individual_perfs = []
            
            for expert in experts:
                base_perf = expected_perf
                
                # Factores mejorados para colaboración
                fatigue_impact = max(0.90, 1.0 - expert.fatigue / 22.0)
                load_impact = max(0.92, 1.0 / (1.0 + expert.load * 0.20))
                domain_bonus = 1.10 if expert.domain in task.required_domains else 1.0
                noise = np.random.normal(0, 0.04)
                
                perf = base_perf * fatigue_impact * load_impact * domain_bonus + noise
                individual_perfs.append(np.clip(perf, 0.55, 0.95))
            
            avg_individual = np.mean(individual_perfs)
            
            # Beneficios de colaboración
            collab_bonus = (synergy - 1.0) * 1.6
            communication_overhead = max(0.98, 1.0 - (len(experts) - 1) * 0.004)
            
            # Bonus por diversidad
            unique_domains = len(set(e.domain for e in experts))
            diversity_bonus = 0.10 * (unique_domains - 1) if unique_domains > 1 else 0
            
            # Balance de carga
            load_balance = self._calculate_load_balance(experts)
            
            # Performance colaborativa
            collab_perf = (avg_individual * (1 + collab_bonus + diversity_bonus) * 
                          communication_overhead * load_balance)
            
            # Chance de rendimiento excepcional
            if np.random.random() < 0.35:
                collab_perf *= np.random.uniform(0.95, 1.05)
            
            # Garantizar mejora mínima
            min_expected = avg_individual * np.random.uniform(1.03, 1.08)
            collab_perf = max(min_expected, collab_perf)
            
            results.append(np.clip(collab_perf, 0.55, 0.95))
        
        return {
            'mean_performance': np.mean(results),
            'std_performance': np.std(results),
            'confidence_interval': np.percentile(results, [15, 85]),
            'success_probability': np.sum(np.array(results) > 0.75) / n_sims,
            'simulation_count': len(results),
            'synergy': synergy
        }
    
    def _calculate_synergy(self, experts: List[Expert], task: Task) -> float:
        """Calcula sinergia entre expertos"""
        if len(experts) < 2:
            return 1.0
        
        # Sinergia base de la matriz
        domains = tuple(sorted([e.domain for e in experts]))
        base_synergy = SYNERGY_MATRIX_BASE.get(domains, SYNERGY_MATRIX_BASE[('default',)])
        
        # Ajustes por historial de colaboración
        collab_adjustment = 1.0
        count = 0
        for i, e1 in enumerate(experts):
            for e2 in experts[i+1:]:
                hist_value = e1.collaboration_history.get(e2.id, 1.0)
                collab_adjustment += hist_value
                count += 1
        
        if count > 0:
            collab_adjustment /= count
        
        return base_synergy * collab_adjustment
    
    def _calculate_load_balance(self, experts: List[Expert]) -> float:
        """Calcula factor de balance de carga"""
        avg_load = np.mean([e.load for e in experts])
        avg_fatigue = np.mean([e.fatigue for e in experts])
        
        balance_factor = 1.0 / (1 + avg_load * 0.6 + 0.05 * avg_fatigue)
        return np.clip(balance_factor, 0.75, 1.0)