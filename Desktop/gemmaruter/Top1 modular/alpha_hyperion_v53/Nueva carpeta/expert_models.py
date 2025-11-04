"""
expert_models.py
Definiciones de expertos y tareas optimizadas
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Expert:
    """Experto con métricas de rendimiento"""
    id: str
    domain: str
    success_rate: float
    computational_cost: float
    availability: float
    specialization_score: float = 1.0
    max_load_capacity: float = 10.0
    recovery_rate: float = 0.15
    efficiency_score: float = 1.0
    
    # Métricas dinámicas
    load: float = 0.0
    fatigue: float = 0.0
    collaboration_history: Dict[str, float] = field(default_factory=dict)
    
    def update_performance(self, performance: float, task_complexity: float):
        """Actualiza métricas después de completar tarea"""
        # Actualizar carga
        load_increase = task_complexity * 0.8
        self.load = min(self.max_load_capacity, self.load + load_increase)
        
        # Actualizar fatiga
        fatigue_increase = task_complexity * 0.5
        self.fatigue = min(self.max_load_capacity * 0.8, self.fatigue + fatigue_increase)
        
        # Recuperación natural
        self.load = max(0, self.load - self.recovery_rate)
        self.fatigue = max(0, self.fatigue - self.recovery_rate * 0.5)
        
        # Ajustar availability
        self.availability = max(0.7, 1.0 - (self.load / self.max_load_capacity) * 0.3)

@dataclass
class Task:
    """Tarea con análisis de requisitos"""
    id: str
    domain_breadth: float
    interdependency: float
    task_scope: float
    required_domains: List[str]
    priority: float = 1.0
    query: str = ""
    
    @property
    def complexity(self) -> float:
        """Complejidad calculada de la tarea"""
        return (0.4 * self.domain_breadth + 
                0.4 * self.interdependency + 
                0.2 * self.task_scope)

class ExpertFactory:
    """Factory para crear expertos con configuraciones predefinidas"""
    
    @staticmethod
    def create_default_experts() -> List[Expert]:
        """Crea el conjunto estándar de expertos"""
        return [
            Expert(
                id="mathstral:7b",
                domain="mathematics",
                success_rate=0.88,
                computational_cost=1.2,
                availability=0.95,
                specialization_score=1.5,
                max_load_capacity=16.0,
                recovery_rate=0.18
            ),
            Expert(
                id="codegemma:2b",
                domain="programming",
                success_rate=0.84,
                computational_cost=0.8,
                availability=0.94,
                specialization_score=1.4,
                max_load_capacity=18.0,
                recovery_rate=0.20
            ),
            Expert(
                id="gemma2:2b",
                domain="language",
                success_rate=0.82,
                computational_cost=0.7,
                availability=0.96,
                specialization_score=1.3,
                max_load_capacity=20.0,
                recovery_rate=0.22
            )
        ]
    
    @staticmethod
    def get_domain_mapping() -> Dict[str, str]:
        """Mapeo estricto de dominios a expertos"""
        return {
            'mathematics': 'mathstral:7b',
            'programming': 'codegemma:2b',
            'language': 'gemma2:2b'
        }

# Matriz de sinergia base para colaboraciones
SYNERGY_MATRIX_BASE = {
    ('mathematics', 'programming'): 1.15,
    ('mathematics', 'language'): 1.08,
    ('programming', 'language'): 1.10,
    ('default',): 1.05
}

# Benchmarks realistas para calibración
BENCHMARK_DATASETS = {
    'mathematics': [
        {'complexity': 0.4, 'domains': ['mathematics'], 'expected_performance': 0.88, 'expert_load': 1.0},
        {'complexity': 0.8, 'domains': ['mathematics'], 'expected_performance': 0.85, 'expert_load': 1.3},
        {'complexity': 1.3, 'domains': ['mathematics', 'programming'], 'expected_performance': 0.82, 'expert_load': 2.0},
    ],
    'programming': [
        {'complexity': 0.5, 'domains': ['programming'], 'expected_performance': 0.84, 'expert_load': 1.1},
        {'complexity': 0.9, 'domains': ['programming'], 'expected_performance': 0.80, 'expert_load': 1.4},
        {'complexity': 1.4, 'domains': ['programming', 'language'], 'expected_performance': 0.76, 'expert_load': 2.2},
    ],
    'language': [
        {'complexity': 0.3, 'domains': ['language'], 'expected_performance': 0.82, 'expert_load': 1.0},
        {'complexity': 0.7, 'domains': ['language', 'mathematics'], 'expected_performance': 0.78, 'expert_load': 1.5},
    ]
}