"""
expert_models.py
Modelos de expertos + matrices de sinergia y benchmarks
Alpha Hyperion v5.3
"""

from dataclasses import dataclass
from typing import List, Dict
import numpy as np

@dataclass
class Task:
    id: str
    domain_breadth: float
    interdependency: float
    task_scope: float
    required_domains: List[str]
    query: str
    complexity: float = 0.0

@dataclass
class Expert:
    id: str
    domain: str
    success_rate: float
    computational_cost: float
    availability: float
    specialization_score: float
    max_load_capacity: float
    recovery_rate: float
    fatigue: float = 0.0

    def update_performance(self, performance: float, complexity: float):
        adjustment = 0.02 * (performance - 0.8) * complexity
        self.success_rate = max(0.5, min(1.0, self.success_rate + adjustment))
        self.fatigue = max(0.0, self.fatigue - self.recovery_rate)
        if self.fatigue > self.max_load_capacity:
            self.availability *= 0.9

# MATRIZ DE SINERGIA BASE (3x3)
SYNERGY_MATRIX_BASE = np.array([
    [1.0, 0.3, 0.2],  # mathstral con: mismo, codegemma, gemma2
    [0.3, 1.0, 0.4],  # codegemma con: mathstral, mismo, gemma2
    [0.2, 0.4, 1.0]   # gemma2 con: mathstral, codegemma, mismo
])

# DATOS DE BENCHMARK (simulados)
BENCHMARK_DATASETS = {
    "mathematics": [
        {"query": "Calcula 17×23", "complexity": 0.3, "domains": ["mathematics"]},
        {"query": "Derivada de x³", "complexity": 0.5, "domains": ["mathematics"]},
        {"query": "Primo 100", "complexity": 0.3, "domains": ["mathematics"]},
    ],
    "programming": [
        {"query": "Inversión de cadena", "complexity": 0.5, "domains": ["programming"]},
        {"query": "Búsqueda binaria", "complexity": 0.45, "domains": ["programming"]},
        {"query": "API Flask", "complexity": 0.4, "domains": ["programming"]},
    ],
    "language": [
        {"query": "Email formal", "complexity": 0.3, "domains": ["language"]},
        {"query": "Traducción inglés", "complexity": 0.4, "domains": ["language"]},
        {"query": "Resumen de texto", "complexity": 0.4, "domains": ["language"]},
    ]
}

class ExpertFactory:
    @staticmethod
    def create_default_experts() -> List[Expert]:
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
                computational_cost=0.6,
                availability=0.96,
                specialization_score=1.3,
                max_load_capacity=12.0,
                recovery_rate=0.25
            ),
            Expert(
                id="gemma2:2b",
                domain="language",
                success_rate=0.82,
                computational_cost=0.7,
                availability=0.97,
                specialization_score=1.3,
                max_load_capacity=14.0,
                recovery_rate=0.22
            )
        ]

    @staticmethod
    def get_domain_mapping() -> dict:
        return {
            "mathematics": "mathstral:7b",
            "programming": "codegemma:2b",
            "language": "gemma2:2b"
        }
