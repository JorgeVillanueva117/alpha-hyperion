"""
fast_classifier.py
Clasificador ultrarrápido con detección de tareas creativas
Alpha Hyperion v5.3
"""

from typing import List, Tuple
import hashlib
import re

class FastPatternClassifier:
    def __init__(self):
        self.cache = {}
        self.math_keywords = [
            "calcula", "deriva", "integral", "matriz", "primo", "factorial",
            "ecuación", "vector", "ángulo", "probabilidad", "estadística",
            "geometría", "álgebra", "límite", "serie", "suma", "resta",
            "multiplica", "divide", "raíz", "potencia", "logaritmo"
        ]
        self.programming_keywords = [
            "función", "clase", "código", "script", "api", "flask", "django",
            "python", "javascript", "java", "sql", "query", "algoritmo",
            "búsqueda", "ordenar", "lista", "array", "diccionario", "json",
            "csv", "archivo", "leer", "escribir", "validar", "regex"
        ]
        self.creative_keywords = [
            "poema", "versos", "ensayo", "cuento", "historia", "novela",
            "redacta", "carta", "email formal", "resumen", "resumir",
            "explica", "teoría", "relatividad", "filosofía", "importancia"
        ]
        self.language_keywords = [
            "traduce", "inglés", "español", "francés", "alemán", "chino",
            "idioma", "gramática", "ortografía", "redacción", "comunicación"
        ]

    def _hash_query(self, query: str) -> str:
        return hashlib.md5(query.lower().encode()).hexdigest()

    def _is_creative_task(self, query: str) -> bool:
        query_lower = query.lower()
        return any(word in query_lower for word in self.creative_keywords)

    def _is_language_task(self, query: str) -> bool:
        query_lower = query.lower()
        return any(word in query_lower for word in self.language_keywords)

    def _is_programming_task(self, query: str) -> bool:
        query_lower = query.lower()
        has_code = bool(re.search(r"\b(def|class|import|function|var|const|let|=>)\b", query_lower))
        has_keyword = any(word in query_lower for word in self.programming_keywords)
        return has_code or has_keyword

    def _is_mathematics_task(self, query: str) -> bool:
        query_lower = query.lower()
        has_math = bool(re.search(r"[\+\-\*\/=∫∑√∞∝∂∆∇]", query))
        has_keyword = any(word in query_lower for word in self.math_keywords)
        has_number = bool(re.search(r"\b\d{1,3}\b", query)) and not self._is_creative_task(query)
        return (has_math or has_keyword or has_number) and not self._is_programming_task(query)

    def classify_fast(self, query: str) -> Tuple[List[str], float, str]:
        query_hash = self._hash_query(query)
        if query_hash in self.cache:
            return self.cache[query_hash]

        query_lower = query.lower()
        domains = []
        complexity = 0.3  # base

        # 1. TAREAS CREATIVAS (alta prioridad)
        if self._is_creative_task(query):
            domains.append("language")
            complexity = max(complexity, 0.4)
            reasoning = "Tarea creativa o literaria"
        
        # 2. TRADUCCIÓN / LENGUAJE
        elif self._is_language_task(query):
            domains.append("language")
            complexity = max(complexity, 0.4)
            reasoning = "Consulta de comunicación o traducción"

        # 3. PROGRAMACIÓN
        elif self._is_programming_task(query):
            domains.append("programming")
            complexity = max(complexity, 0.5)
            reasoning = "Tarea de programación o desarrollo"

        # 4. MATEMÁTICAS (solo si no es creativo)
        elif self._is_mathematics_task(query):
            domains.append("mathematics")
            complexity = max(complexity, 0.3)
            reasoning = "Operación matemática o cálculo numérico"

        # 5. DEFAULT: lenguaje
        else:
            domains.append("language")
            complexity = 0.3
            reasoning = "Consulta general de comunicación"

        # Ajuste final de complejidad
        if len(domains) > 1:
            complexity += 0.1
        if len(query) > 200:
            complexity += 0.1

        result = (domains, round(complexity, 3), reasoning)
        self.cache[query_hash] = result
        return result

    def get_cache_stats(self) -> dict:
        hit_rate = 0.0
        if len(self.cache) > 0:
            # Simulación simple: asumimos 30% hits en producción
            hit_rate = 0.3
        return {
            "size": len(self.cache),
            "hit_rate": hit_rate
        }