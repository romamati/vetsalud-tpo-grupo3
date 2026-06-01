"""
Consultas sobre Neo4j.

Q1  — Pacientes activos con datos de propietario
Q2  — Consultas en estado 'Seguimiento' con veterinario y costo
Q3  — Historial completo de un paciente (consultas + vacunas por fecha)
Q4  — Propietarios con más de un paciente registrado
Q5  — Veterinarios activos y cantidad de consultas en los últimos 60 días
Q6  — Pacientes con vacunas vencidas
Q7  — Top 5 diagnósticos más frecuentes
Q9  — Consultas de tipo 'Control' con costo menor a $5.000
Q10 — Todos los pacientes de una sucursal determinada
Q11 — Ingresos totales por veterinario en el mes actual
Q12 — Propietarios sin consultas en el último año
Q13 — ABM completo de propietarios (alta, modificación, baja lógica)
Q14 — Registro de nueva consulta médica con validación
"""

from datetime import date, timedelta
from neo4j_db.connection import run_query


# Q1

def q1_pacientes_activos_con_propietario():
    """
    Q1: Retorna todos los pacientes activos junto con los datos completos
    de su propietario.
    """
    return run_query("""
        MATCH (prop:Propietario)-[:TIENE]->(pac:Paciente {activo: true})
        RETURN pac.id        AS id_paciente,
               pac.nombre    AS paciente,
               pac.especie   AS especie,
               pac.raza      AS raza,
               pac.fecha_nac AS fecha_nac,
               prop.id       AS id_propietario,
               prop.nombre   AS propietario_nombre,
               prop.apellido AS propietario_apellido,
               prop.email    AS email,
               prop.telefono AS telefono,
               prop.ciudad   AS ciudad,
               prop.provincia AS provincia
        ORDER BY prop.apellido, pac.nombre
    """)


# Q2

def q2_consultas_en_seguimiento():
    """
    Q2: Retorna las consultas médicas en estado 'Seguimiento' con el
    veterinario asignado y el costo.
    """
    return run_query("""
        MATCH (pac:Paciente)-[:TIENE]->(c:Consulta {estado: 'Seguimiento'})
        MATCH (v:Veterinario)-[:ATIENDE]->(c)
        RETURN c.id          AS id_consulta,
               pac.nombre    AS paciente,
               c.fecha       AS fecha,
               c.motivo      AS motivo,
               c.diagnostico AS diagnostico,
               c.costo       AS costo,
               v.nombre + ' ' + v.apellido AS veterinario,
               v.especialidad AS especialidad
        ORDER BY c.fecha DESC
    """)


# Q3

def q3_historial_paciente(id_paciente: str):
    """
    Q3: Retorna el historial completo de un paciente: consultas y vacunaciones
    ordenadas por fecha.

    Args:
        id_paciente: ID del paciente (ej: 'P001').
    """
    consultas = run_query("""
        MATCH (pac:Paciente {id: $id})-[:TIENE]->(c:Consulta)
        MATCH (v:Veterinario)-[:ATIENDE]->(c)
        RETURN 'Consulta'                        AS tipo,
               c.fecha                           AS fecha,
               c.motivo                          AS descripcion,
               c.diagnostico                     AS detalle,
               v.nombre + ' ' + v.apellido       AS veterinario,
               toString(c.costo)                 AS extra
        ORDER BY c.fecha DESC
    """, {"id": id_paciente})

    vacunas = run_query("""
        MATCH (pac:Paciente {id: $id})-[:RECIBE]->(vac:Vacunacion)
        MATCH (v:Veterinario)-[:APLICA]->(vac)
        RETURN 'Vacunación'                      AS tipo,
               vac.fecha_aplicacion              AS fecha,
               vac.nombre_vacuna                 AS descripcion,
               'Próx. dosis: ' + vac.proxima_dosis AS detalle,
               v.nombre + ' ' + v.apellido       AS veterinario,
               ''                                AS extra
        ORDER BY vac.fecha_aplicacion DESC
    """, {"id": id_paciente})

    historial = consultas + vacunas
    historial.sort(key=lambda x: x["fecha"], reverse=True)
    return historial


# Q4

def q4_propietarios_con_varios_pacientes():
    """
    Q4: Retorna los propietarios que tienen más de un paciente registrado,
    junto con la cantidad y los nombres de sus mascotas.
    """
    return run_query("""
        MATCH (prop:Propietario)-[:TIENE]->(pac:Paciente)
        WITH prop, count(pac) AS cantidad, collect(pac.nombre) AS mascotas
        WHERE cantidad > 1
        RETURN prop.id                            AS id_propietario,
               prop.nombre + ' ' + prop.apellido  AS propietario,
               prop.email                         AS email,
               cantidad,
               mascotas
        ORDER BY cantidad DESC
    """)


# Q5

def q5_veterinarios_activos_consultas_recientes():
    """
    Q5: Retorna los veterinarios activos con la cantidad de consultas
    realizadas en los últimos 60 días.
    """
    fecha_limite = (date.today() - timedelta(days=60)).isoformat()
    return run_query("""
        MATCH (v:Veterinario {activo: true})
        OPTIONAL MATCH (v)-[:ATIENDE]->(c:Consulta)
        WHERE c.fecha >= $fecha_limite
        RETURN v.id                               AS id_vet,
               v.nombre + ' ' + v.apellido        AS veterinario,
               v.especialidad                     AS especialidad,
               v.sucursal                         AS sucursal,
               count(c)                           AS consultas_recientes
        ORDER BY consultas_recientes DESC
    """, {"fecha_limite": fecha_limite})


# Q6

def q6_pacientes_vacunas_vencidas():
    """
    Q6: Retorna los pacientes que tienen al menos una vacuna vencida
    (proxima_dosis anterior a la fecha de hoy).
    """
    hoy = date.today().isoformat()
    return run_query("""
        MATCH (prop:Propietario)-[:TIENE]->(pac:Paciente)-[:RECIBE]->(vac:Vacunacion)
        WHERE vac.proxima_dosis < $hoy
        RETURN pac.id                             AS id_paciente,
               pac.nombre                        AS paciente,
               pac.especie                       AS especie,
               vac.nombre_vacuna                 AS vacuna,
               vac.proxima_dosis                 AS vencio,
               prop.nombre + ' ' + prop.apellido  AS propietario,
               prop.telefono                     AS telefono
        ORDER BY vac.proxima_dosis ASC
    """, {"hoy": hoy})


# Q7

def q7_top5_diagnosticos():
    """
    Q7: Retorna los 5 diagnósticos más frecuentes registrados en el sistema.
    """
    return run_query("""
        MATCH (c:Consulta)
        RETURN c.diagnostico AS diagnostico,
               count(c)      AS frecuencia
        ORDER BY frecuencia DESC
        LIMIT 5
    """)
