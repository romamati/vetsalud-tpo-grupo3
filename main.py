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
    q9_consultas_control_economicas,
    q10_pacientes_por_sucursal,
    q11_ingresos_por_veterinario_mes_actual,
    q12_propietarios_sin_consultas_ultimo_anio,
    q13_alta_propietario,
    q13_modificar_propietario,
    q13_baja_logica_propietario,
    q14_registrar_consulta,
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

def handle_q9():
    print("\n📋 Consultas de tipo 'Control' con costo < $5.000\n")
    resultados = q9_consultas_control_economicas()
    for r in resultados:
        print(f"  {r['id_consulta']} | {r['paciente']:10s} | "
              f"{r['fecha']} | ${r['costo']:>6.0f} | {r['veterinario']}")
    print(f"\n  Total: {len(resultados)} consultas.")


def handle_q10():
    sucursal = input("\n  Ingresá la sucursal (Palermo / Belgrano / Caballito): ").strip()
    print(f"\n📋 Pacientes atendidos en {sucursal}\n")
    resultados = q10_pacientes_por_sucursal(sucursal)
    if not resultados:
        print(f"  No se encontraron pacientes para la sucursal '{sucursal}'.")
        return
    for r in resultados:
        print(f"  {r['paciente']:10s} ({r['especie']:8s}) → {r['propietario']} | {r['telefono']}")
    print(f"\n  Total: {len(resultados)} pacientes.")


def handle_q11():
    print("\n📋 Ingresos por veterinario — mes actual\n")
    resultados = q11_ingresos_por_veterinario_mes_actual()
    if not resultados:
        print("  No hay consultas registradas en el mes actual.")
        return
    for r in resultados:
        print(f"  {r['veterinario']:25s} | {r['sucursal']:10s} | "
              f"{r['cantidad_consultas']} consultas | ${r['ingresos_totales']:>10.0f}")


def handle_q12():
    print("\n📋 Propietarios sin consultas en el último año\n")
    resultados = q12_propietarios_sin_consultas_ultimo_anio()
    if not resultados:
        print("  Todos los propietarios tienen consultas recientes. ✅")
        return
    for r in resultados:
        print(f"  {r['propietario']:25s} | {r['email']:30s} | Pacientes: {r['pacientes']}")
    print(f"\n  Total: {len(resultados)} propietarios sin actividad reciente.")


def handle_q13():
    print("\n📋 ABM de Propietarios\n")
    print("  [A] Alta — nuevo propietario")
    print("  [M] Modificación — actualizar datos")
    print("  [B] Baja lógica — desactivar propietario")
    op = input("\n  Elegí una opción (A/M/B): ").strip().upper()

    if op == "A":
        print("\n  Completá los datos del nuevo propietario:")
        datos = {
            "id":        input("  ID (ej: C017): ").strip(),
            "nombre":    input("  Nombre: ").strip(),
            "apellido":  input("  Apellido: ").strip(),
            "dni":       input("  DNI: ").strip(),
            "email":     input("  Email: ").strip(),
            "telefono":  input("  Teléfono: ").strip(),
            "ciudad":    input("  Ciudad: ").strip(),
            "provincia": input("  Provincia: ").strip(),
        }
        resultado = q13_alta_propietario(datos)
        print(f"\n  {'✅' if resultado['ok'] else '❌'} {resultado['mensaje']}")

    elif op == "M":
        id_prop = input("\n  ID del propietario a modificar: ").strip()
        print("  Ingresá los campos a actualizar (Enter para no cambiar):")
        campos = {}
        for campo in ["nombre", "apellido", "email", "telefono", "ciudad", "provincia"]:
            val = input(f"  {campo.capitalize()}: ").strip()
            if val:
                campos[campo] = val
        resultado = q13_modificar_propietario(id_prop, campos)
        print(f"\n  {'✅' if resultado['ok'] else '❌'} {resultado['mensaje']}")

    elif op == "B":
        id_prop = input("\n  ID del propietario a dar de baja: ").strip()
        confirmar = input(f"  ¿Confirmás la baja lógica de '{id_prop}'? (s/n): ").strip().lower()
        if confirmar == "s":
            resultado = q13_baja_logica_propietario(id_prop)
            print(f"\n  {'✅' if resultado['ok'] else '❌'} {resultado['mensaje']}")
        else:
            print("\n  Operación cancelada.")
    else:
        print("\n  Opción no válida.")


def handle_q14():
    print("\n📋 Registrar nueva consulta médica\n")
    datos = {
        "id_consulta": input("  ID de consulta (ej: CON019): ").strip(),
        "id_paciente": input("  ID del paciente (ej: P001): ").strip().upper(),
        "id_vet":      input("  ID del veterinario (ej: V001): ").strip().upper(),
        "fecha":       input("  Fecha (YYYY-MM-DD): ").strip(),
        "motivo":      input("  Motivo: ").strip(),
        "diagnostico": input("  Diagnóstico: ").strip(),
        "costo":       float(input("  Costo: $").strip()),
        "estado":      input("  Estado (Cerrada / Seguimiento): ").strip(),
    }
    resultado = q14_registrar_consulta(datos)
    print(f"\n  {'✅' if resultado['ok'] else '❌'} {resultado['mensaje']}")


if __name__ == "__main__":
    main()