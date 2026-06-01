"""
main.py
Punto de entrada principal del sistema VetSalud.
"""

from mongodb_db.connection import close_connection as mongo_close
from neo4j_db.connection import close_connection as neo4j_close

from queries.neo4j_queries import (
    q1_pacientes_activos_con_propietario,
    q2_consultas_en_seguimiento,
    q3_historial_paciente,
    q4_propietarios_con_varios_pacientes,
    q5_veterinarios_activos_consultas_recientes,
    q6_pacientes_vacunas_vencidas,
    q7_top5_diagnosticos,
)
from queries.mongodb_queries import (
    q8_stock_bajo,
    q15_actualizar_stock,
)


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


# Helpers de presentación

def separador():
    print("\n" + "─" * 55)


def pausar():
    input("\n  Presioná Enter para continuar...")


# Handlers de cada consulta

def handle_q1():
    print("\n📋 Pacientes activos con datos de propietario\n")
    resultados = q1_pacientes_activos_con_propietario()
    for r in resultados:
        print(f"  {r['paciente']:10s} ({r['especie']:8s}) → "
              f"{r['propietario_nombre']} {r['propietario_apellido']} | "
              f"{r['ciudad']} | {r['email']}")
    print(f"\n  Total: {len(resultados)} pacientes activos.")


def handle_q2():
    print("\n📋 Consultas en estado Seguimiento\n")
    resultados = q2_consultas_en_seguimiento()
    for r in resultados:
        print(f"  {r['id_consulta']} | {r['paciente']:10s} | "
              f"{r['diagnostico']:25s} | ${r['costo']:>8.0f} | {r['veterinario']}")
    print(f"\n  Total: {len(resultados)} consultas en seguimiento.")


def handle_q3():
    id_pac = input("\n  Ingresá el ID del paciente (ej: P001): ").strip().upper()
    print(f"\n📋 Historial completo de {id_pac}\n")
    resultados = q3_historial_paciente(id_pac)
    if not resultados:
        print("  No se encontraron registros para ese paciente.")
        return
    for r in resultados:
        print(f"  [{r['tipo']:10s}] {r['fecha']} | {r['descripcion']:25s} | {r['detalle']}")
    print(f"\n  Total: {len(resultados)} registros.")


def handle_q4():
    print("\n📋 Propietarios con más de un paciente\n")
    resultados = q4_propietarios_con_varios_pacientes()
    for r in resultados:
        print(f"  {r['propietario']:25s} → {r['cantidad']} mascotas: {r['mascotas']}")
    print(f"\n  Total: {len(resultados)} propietarios.")


def handle_q5():
    print("\n📋 Veterinarios activos — consultas en los últimos 60 días\n")
    resultados = q5_veterinarios_activos_consultas_recientes()
    for r in resultados:
        print(f"  {r['veterinario']:25s} | {r['sucursal']:10s} | "
              f"{r['especialidad']:20s} | {r['consultas_recientes']} consultas")


def handle_q6():
    print("\n📋 Pacientes con vacunas vencidas\n")
    resultados = q6_pacientes_vacunas_vencidas()
    if not resultados:
        print("  No hay vacunas vencidas. ✅")
        return
    for r in resultados:
        print(f"  {r['paciente']:10s} | {r['vacuna']:20s} | "
              f"venció: {r['vencio']} | Contacto: {r['propietario']} ({r['telefono']})")
    print(f"\n  Total: {len(resultados)} vacunas vencidas.")


def handle_q7():
    print("\n📋 Top 5 diagnósticos más frecuentes\n")
    for i, r in enumerate(q7_top5_diagnosticos(), 1):
        print(f"  {i}. {r['diagnostico']:30s} → {r['frecuencia']} veces")


if __name__ == "__main__":
    main()