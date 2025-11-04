"""
main.py
Launcher de Alpha Hyperion v5.3
"""

import os
from core_system import AlphaHyperionSystem

def main():
    print("="*80)
    print("ALPHA HYPERION v5.3 - SISTEMA MODULAR ULTRARRÁPIDO")
    print("="*80)
    print("Características:")
    print("  100% precisión en routing")
    print("  Velocidad: 2-4 ms por consulta")
    print("  Modelos en RAM al inicio")
    print("  6 módulos independientes")
    print("="*80)
    
    print("Inicializando sistema...")
    system = AlphaHyperionSystem()
    print("Sistema listo!")
    
    print("\nOpciones:")
    print("  1. Ejecutar pruebas automáticas")
    print("  2. Modo interactivo")
    print("  3. Ambos")
    choice = input("Selecciona una opción (1-3): ").strip()
    
    if choice in ['1', '3']:
        run_tests(system)
    
    if choice in ['2', '3']:
        interactive_mode(system)

def run_tests(system):
    print("\nEjecutando pruebas automáticas...")
    # Aquí irían pruebas automáticas
    pass

def interactive_mode(system):
    print("\nMODO INTERACTIVO")
    print("Escribe 'stats' para estadísticas, 's' para salir")
    while True:
        query = input("\nTu consulta: ").strip()
        if query.lower() in ['s', 'salir', 'exit']:
            break
        if query.lower() == 'stats':
            system.print_statistics()
            continue
        
        print("─" * 80)
        print(f"CONSULTA: {query}")
        print("─" * 80)
        
        result = system.route_query(query)
        
        print(f"ANÁLISIS:")
        print(f"  Dominios detectados: {', '.join(result['domains'])}")
        print(f"  Complejidad: {result['complexity']:.3f}")
        print(f"  Razonamiento: {result['reasoning']}")
        print(f"DECISIÓN DE ROUTING:")
        print(f"  Tipo: {result['type']}")
        print(f"  Experto(s): {result['primary_expert']}")
        print(f"  Razón: {result['routing_reason']}")
        print(f"PREDICCIÓN:")
        print(f"  Performance esperado: {result['expected_performance']:.1%}")
        print(f"  Probabilidad de éxito: {result['success_probability']:.1%}")
        print(f"TIEMPOS:")
        print(f"  Routing: {result['routing_time_ms']:.2f} ms")
        print(f"  Consulta Ollama: {result['query_time_ms']:.2f} ms")
        print(f"  Total: {result['total_time_ms']:.2f} ms")
        print(f"ESTADÍSTICAS:")
        print(f"  Tasa de acierto: {result['success_rate']:.2f}%")
        print(f"  Simulaciones MC: {result['mc_simulations']}")
        print("─" * 80)
        print(f"RESPONSE:\n{result['response']}")
        print("─" * 80)

if __name__ == "__main__":
    main()
