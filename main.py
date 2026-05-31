"""
main.py
Punto de entrada principal del sistema VetSalud.
Grupo 3 — VetSalud TPO BD2 2026
"""

from mongodb.connection import close_connection as mongo_close
from neo4j.connection import close_connection as neo4j_close


def menu():
    print("\n" + "=" * 55)
    print("       🐾  VetSalud S.A. — Sistema de Gestión")
    print("=" * 55)
    print("  [1]  Pacientes activos con datos de propietario")
    print("  [2]  Consultas en estado Seguimiento")
    print("  [3]  Historial completo de un paciente")
    print("  [4]  Propietarios con más de un paciente")
    print("  [5]  Veterinarios activos y consultas (60 días)")
    print("  [6]  Pacientes con vacunas vencidas")
    print("  [7]  Top 5 diagnósticos más frecuentes")
    print("  [8]  Stock bajo (< 50 unidades)")
    print("  [9]  Consultas 'Control' con costo < $5.000")
    print(" [10]  Pacientes por sucursal")
    print(" [11]  Ingresos por veterinario (mes actual)")
    print(" [12]  Propietarios sin consultas (último año)")
    print(" [13]  ABM de propietarios")
    print(" [14]  Registrar nueva consulta médica")
    print(" [15]  Actualizar stock tras consulta")
    print("  [0]  Salir")
    print("=" * 55)
    return input("  Seleccione una opción: ").strip()


def main():
    print("\n🐾 Iniciando VetSalud S.A. ...")
    try:
        while True:
            opcion = menu()
            if opcion == "0":
                print("\n👋 Cerrando conexiones y saliendo. ¡Hasta luego!")
                break
            else:
                print(f"\n⚠️  Consulta [{opcion}] aún no implementada. Próximamente.")
    finally:
        mongo_close()
        neo4j_close()


if __name__ == "__main__":
    main()