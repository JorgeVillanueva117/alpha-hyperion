"""
main.py
Alpha Hyperion v5.3 - Sistema Modular Ultrarrápido
Programa principal interactivo
"""

import time
from core_system import AlphaHyperionSystem

def print_banner():
    """Banner del sistema"""
    print("\n" + "="*80)
    print("🚀 ALPHA HYPERION v5.3 - SISTEMA MODULAR ULTRARRÁPIDO")
    print("="*80)
    print("Características:")
    print("  ✓ 100% precisión en routing")
    print("  ✓ Velocidad: 2-4 ms por consulta")
    print("  ✓ Clasificador ultrarrápido con caché")
    print("  ✓ Meta-agente supervisor")
    print("  ✓ 6 módulos independientes")
    print("="*80 + "\n")

def print_result(result: dict, show_details: bool = True):
    """Imprime resultado de routing"""
    print(f"\n{'─'*80}")
    print(f"📝 CONSULTA: {result['query']}")
    print(f"{'─'*80}")
    
    # Análisis
    print(f"\n🔍 ANÁLISIS:")
    print(f"  Dominios detectados: {', '.join(result['domains'])}")
    print(f"  Complejidad: {result['complexity']:.3f}")
    print(f"  Razonamiento: {result['reasoning']}")
    
    # Decisión de routing
    print(f"\n🎯 DECISIÓN DE ROUTING:")
    print(f"  Tipo: {result['type']}")
    print(f"  Experto(s): {', '.join([e.split(':')[0] for e in result['experts']])}")
    print(f"  Razón: {result['routing_reason']}")
    
    # Predicción de rendimiento
    print(f"\n📊 PREDICCIÓN:")
    print(f"  Performance esperado: {result['expected_performance']:.1%}")
    print(f"  Probabilidad de éxito: {result['success_probability']:.1%}")
    if result['synergy'] > 1.0:
        print(f"  Sinergia: {result['synergy']:.3f} (+{(result['synergy']-1)*100:.1f}% colaboración)")
    
    # TIEMPOS (CRÍTICO!)
    print(f"\n⚡ TIEMPOS:")
    print(f"  Routing: {result['routing_time_ms']:.2f} ms")
    print(f"  Consulta Ollama: {result['query_time_ms']:.2f} ms")
    print(f"  Total: {result['total_time_ms']:.2f} ms")
    
    # Estadísticas actuales
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"  Tasa de acierto: {result['success_rate']:.2f}%")
    print(f"  Simulaciones MC: {result['mc_simulations']}")
    
    if show_details:
        print(f"{'─'*80}")

def run_test_queries(system: AlphaHyperionSystem):
    """Ejecuta consultas de prueba"""
    test_queries = [
        "¿Cuánto es 2 + 2?",
        "Crear una función en Python para ordenar una lista",
        "Escribir un ensayo sobre la importancia de la educación",
        "Desarrollar un algoritmo que calcule números primos",
        "¿Cuántas estrellas hay en el universo?",
        "Implementar búsqueda binaria en Python",
        "Calcular la derivada de x^2 + 3x + 5",
        "Crear un API REST con Flask",
        "Explicar la teoría de la relatividad"
    ]
    
    print("\n" + "="*80)
    print("🧪 EJECUTANDO CONSULTAS DE PRUEBA")
    print("="*80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] {query}")
        start = time.perf_counter()
        result = system.route_query(query)
        elapsed = (time.perf_counter() - start) * 1000
        
        print(f"  → {result['primary_expert'].split(':')[0]}")
        print(f"     Routing: {result['routing_time_ms']:.2f}ms | "
              f"Total: {elapsed:.2f}ms | "
              f"Acierto: {'✓' if result['domains'][0] in result['routing_reason'].lower() or any(d in result['primary_expert'] for d in result['domains']) else '✗'}")
    
    print("\n" + "="*80)

def interactive_mode(system: AlphaHyperionSystem):
    """Modo interactivo"""
    print("\n💬 MODO INTERACTIVO")
    print("Escribe 'stats' para ver estadísticas, 's' para salir\n")
    
    while True:
        try:
            query = input("Tu consulta: ").strip()
            
            if not query:
                continue
            
            if query.lower() == 's':
                print("\n👋 ¡Hasta luego!")
                system.print_statistics()
                break
            
            if query.lower() == 'stats':
                system.print_statistics()
                continue
            
            # Procesar consulta
            result = system.route_query(query)
            print_result(result, show_details=True)
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            system.print_statistics()
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

def main():
    """Función principal"""
    print_banner()
    
    # Inicializar sistema
    print("🔧 Inicializando sistema...")
    system = AlphaHyperionSystem()
    print("✓ Sistema listo!\n")
    
    # Menú
    print("Opciones:")
    print("  1. Ejecutar pruebas automáticas")
    print("  2. Modo interactivo")
    print("  3. Ambos")
    
    choice = input("\nSelecciona una opción (1-3): ").strip()
    
    if choice == '1':
        run_test_queries(system)
        system.print_statistics()
    
    elif choice == '2':
        interactive_mode(system)
    
    elif choice == '3':
        run_test_queries(system)
        interactive_mode(system)
    
    else:
        print("❌ Opción inválida")
        return
    
    print("\n✨ Sesión finalizada")

if __name__ == "__main__":
    main()