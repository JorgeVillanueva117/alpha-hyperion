"""
fast_classifier.py
Clasificador ultrarrápido basado en patrones y heurísticas
Velocidad objetivo: < 1 ms por clasificación
"""

import re
import time
from typing import Dict, List, Tuple
from collections import defaultdict

class FastPatternClassifier:
    """Clasificador de patrones ultrarrápido con caché"""
    
    def __init__(self):
        # Patrones compilados para máxima velocidad
        self.math_patterns = [
            re.compile(r'\b\d+\s*[\+\-\*/\^\%]\s*\d+\b'),
            re.compile(r'\b(calcul|derivad|integral|ecuaci[oó]n|matriz|vector)\b', re.I),
            re.compile(r'\b(factorial|fibonacci|primo|logaritmo|exponencial)\b', re.I),
            re.compile(r'\b(suma|resta|multiplica|divide|raíz|potencia)\b', re.I),
        ]
        
        self.prog_patterns = [
            re.compile(r'\b(función|funcion|def|class|import|return)\b', re.I),
            re.compile(r'\b(algoritmo|código|codigo|programa|script)\b', re.I),
            re.compile(r'\b(python|javascript|java|c\+\+|sql|api)\b', re.I),
            re.compile(r'\b(base de datos|servidor|cliente|request)\b', re.I),
            re.compile(r'\b(ordenar|buscar|filtrar|parsear|validar)\b', re.I),
        ]
        
        self.lang_patterns = [
            re.compile(r'\b(escrib|redact|ensayo|artículo|texto)\b', re.I),
            re.compile(r'\b(por qué|cómo|cuándo|dónde|quién)\b', re.I),
            re.compile(r'\b(explicar|describir|analizar|resumir)\b', re.I),
        ]
        
        # Caché de clasificaciones
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Palabras clave ponderadas (velocidad > precisión marginal)
        self.keyword_weights = {
            'mathematics': {
                'calcular': 0.9, 'derivada': 0.95, 'integral': 0.95,
                'ecuación': 0.9, 'matriz': 0.9, 'suma': 0.8, 'resta': 0.8,
                'multiplicar': 0.8, 'dividir': 0.8, 'factorial': 0.9,
                'primo': 0.85, 'fibonacci': 0.85, '=': 0.7
            },
            'programming': {
                'función': 0.95, 'algoritmo': 0.95, 'código': 0.9,
                'programa': 0.85, 'python': 0.9, 'ordenar': 0.85,
                'api': 0.85, 'base de datos': 0.9, 'script': 0.85,
                'implementar': 0.8, 'desarrollar': 0.8, 'crear': 0.7
            },
            'language': {
                'escribir': 0.9, 'ensayo': 0.95, 'redactar': 0.9,
                'explicar': 0.85, 'describir': 0.85, 'por qué': 0.8,
                'cómo': 0.75, 'artículo': 0.9
            }
        }
    
    def classify_fast(self, query: str) -> Tuple[List[str], float, str]:
        """
        Clasificación ultrarrápida
        Returns: (dominios, complejidad, razonamiento)
        """
        start_time = time.perf_counter()
        
        # Verificar caché primero
        cache_key = query.lower().strip()
        if cache_key in self.cache:
            self.cache_hits += 1
            return self.cache[cache_key]
        
        self.cache_misses += 1
        query_lower = query.lower()
        
        # Scoring rápido por dominio
        scores = {'mathematics': 0.0, 'programming': 0.0, 'language': 0.0}
        
        # 1. Patrones regex (rápido)
        for pattern in self.math_patterns:
            if pattern.search(query_lower):
                scores['mathematics'] += 0.3
        
        for pattern in self.prog_patterns:
            if pattern.search(query_lower):
                scores['programming'] += 0.3
        
        for pattern in self.lang_patterns:
            if pattern.search(query_lower):
                scores['language'] += 0.3
        
        # 2. Keywords ponderadas (muy rápido)
        for domain, keywords in self.keyword_weights.items():
            for keyword, weight in keywords.items():
                if keyword in query_lower:
                    scores[domain] += weight
        
        # 3. Heurísticas rápidas
        if any(char.isdigit() for char in query):
            scores['mathematics'] += 0.2
        
        if 'función' in query_lower or 'crear' in query_lower:
            if 'python' in query_lower or 'código' in query_lower:
                scores['programming'] += 0.4
        
        # Determinar dominios (threshold bajo para velocidad)
        threshold = 0.4
        detected_domains = [d for d, s in scores.items() if s >= threshold]
        
        # Fallback inteligente
        if not detected_domains:
            max_domain = max(scores.items(), key=lambda x: x[1])
            if max_domain[1] > 0.1:
                detected_domains = [max_domain[0]]
            else:
                # Heurística final por contexto
                if any(op in query for op in ['+', '-', '*', '/', '=']):
                    detected_domains = ['mathematics']
                elif 'función' in query_lower or 'código' in query_lower:
                    detected_domains = ['programming']
                else:
                    detected_domains = ['language']
        
        # Calcular complejidad (simplificado para velocidad)
        complexity = self._calculate_complexity_fast(query, detected_domains, scores)
        
        # Razonamiento breve
        reasoning = self._generate_reasoning_fast(detected_domains, scores, query)
        
        result = (detected_domains, complexity, reasoning)
        
        # Almacenar en caché (con límite)
        if len(self.cache) < 1000:
            self.cache[cache_key] = result
        
        return result
    
    def _calculate_complexity_fast(self, query: str, domains: List[str], scores: Dict) -> float:
        """Cálculo rápido de complejidad"""
        base_complexity = 0.3
        
        # Multi-dominio = más complejo
        if len(domains) > 1:
            base_complexity += 0.2
        
        # Longitud de query
        word_count = len(query.split())
        if word_count > 15:
            base_complexity += 0.15
        elif word_count > 8:
            base_complexity += 0.1
        
        # Palabras clave de complejidad
        complex_keywords = ['algoritmo', 'optimizar', 'avanzado', 'complejo', 'sistema']
        for kw in complex_keywords:
            if kw in query.lower():
                base_complexity += 0.15
                break
        
        # Ajuste por scores
        max_score = max(scores.values())
        if max_score > 1.5:
            base_complexity += 0.1
        
        return min(1.0, max(0.2, base_complexity))
    
    def _generate_reasoning_fast(self, domains: List[str], scores: Dict, query: str) -> str:
        """Genera razonamiento breve"""
        if len(domains) == 1:
            domain = domains[0]
            if domain == 'mathematics':
                return "Operación matemática o cálculo numérico"
            elif domain == 'programming':
                return "Tarea de programación o desarrollo"
            else:
                return "Consulta de comunicación o redacción"
        else:
            return f"Tarea multi-dominio: {', '.join(domains)}"
    
    def get_cache_stats(self) -> Dict:
        """Estadísticas del caché"""
        total = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total if total > 0 else 0
        return {
            'cache_size': len(self.cache),
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': hit_rate
        }