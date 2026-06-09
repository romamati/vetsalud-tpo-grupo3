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

#Helpers

def _siguiente_id_neo4j(label: str, prefijo: str, ancho: int = 3) -> str:
    """
    Genera el próximo ID incremental para un label de Neo4j.

    Ejemplos:
        Propietario + C   -> C007
        Veterinario + V   -> V006
        Consulta + CON    -> CON009
        Vacunacion + VAC  -> VAC007
    """
    resultado = run_query(f"""
        MATCH (n:{label})
        WHERE n.id STARTS WITH $prefijo
        WITH max(toInteger(replace(n.id, $prefijo, ''))) AS max_numero
        RETURN coalesce(max_numero, 0) + 1 AS siguiente
    """, {"prefijo": prefijo})

    siguiente = resultado[0]["siguiente"] if resultado else 1
    return f"{prefijo}{int(siguiente):0{ancho}d}"

def _validar_campos_requeridos(datos: dict, campos: list[str]) -> str | None:
    """Devuelve el nombre del primer campo obligatorio vacío, o None si todo está OK."""
    for campo in campos:
        if not str(datos.get(campo, "")).strip():
            return campo
    return None

def _normalizar_estado_consulta(estado: str) -> str:
    """Normaliza el estado de una consulta a los valores usados por el sistema."""
    estado_limpio = str(estado or "").strip().lower()
    if estado_limpio in {"cerrada", "cerrado"}:
        return "Cerrada"
    if estado_limpio == "seguimiento":
        return "Seguimiento"
    return str(estado or "").strip()



# Q1

def q1_pacientes_activos_con_propietario():
    """
    Q1: Retorna todos los pacientes activos junto con los datos completos
    de su propietario.
    """
    return run_query("""
        MATCH (prop:Propietario)-[:TIENE]->(pac:Paciente {activo: true})
        RETURN pac.id         AS id_paciente,
               pac.nombre     AS paciente,
               pac.especie    AS especie,
               prop.id        AS id_propietario,
               prop.nombre    AS propietario_nombre,
               prop.apellido  AS propietario_apellido,
               prop.email     AS email,
               prop.telefono  AS telefono,
               prop.ciudad    AS ciudad,
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
        RETURN c.id                        AS id_consulta,
               pac.id                      AS id_paciente,
               pac.nombre                  AS paciente,
               c.fecha                     AS fecha,
               c.diagnostico               AS diagnostico,
               c.costo                     AS costo,
               v.id                        AS id_veterinario,
               v.nombre + ' ' + v.apellido AS veterinario
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
               c.id                              AS id,
               c.fecha                           AS fecha,
               c.motivo                          AS descripcion,
               'Diagnóstico: ' + c.diagnostico   AS detalle
        ORDER BY c.fecha DESC
    """, {"id": id_paciente})

    vacunas = run_query("""
        MATCH (pac:Paciente {id: $id})-[:RECIBE]->(vac:Vacunacion)
        MATCH (v:Veterinario)-[:APLICA]->(vac)
        RETURN 'Vacunación'                        AS tipo,
               vac.id                              AS id,
               vac.fecha_aplicacion                AS fecha,
               vac.nombre_vacuna                   AS descripcion,
               'Próx. dosis: ' + vac.proxima_dosis AS detalle
        ORDER BY vac.fecha_aplicacion DESC
    """, {"id": id_paciente})

    historial = consultas + vacunas
    historial.sort(key=lambda x: x["fecha"], reverse=True)
    return historial


# Q4

def q4_propietarios_con_varios_pacientes():
    """
    Q4: Retorna los propietarios que tienen más de un paciente registrado,
    junto con la cantidad y los datos de sus pacientes.
    """
    return run_query("""
        MATCH (prop:Propietario)-[:TIENE]->(pac:Paciente)
        WITH prop,
             count(pac) AS cantidad,
             collect({id_paciente: pac.id, paciente: pac.nombre}) AS mascotas
        WHERE cantidad > 1
        RETURN prop.id                            AS id_propietario,
               prop.nombre + ' ' + prop.apellido  AS propietario,
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
               pac.nombre                         AS paciente,
               vac.nombre_vacuna                  AS vacuna,
               vac.proxima_dosis                  AS vencio,
               prop.id                            AS id_propietario,
               prop.nombre + ' ' + prop.apellido  AS propietario,
               prop.telefono                      AS telefono
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

# Q9

def q9_consultas_control_economicas():
    """
    Q9: Retorna las consultas de tipo 'Control' con costo menor a $5.000.
    """
    return run_query("""
        MATCH (pac:Paciente)-[:TIENE]->(c:Consulta)
        MATCH (v:Veterinario)-[:ATIENDE]->(c)
        WHERE toLower(c.motivo) CONTAINS 'control'
          AND c.costo < 5000
        RETURN c.id                               AS id_consulta,
               pac.id                             AS id_paciente,
               pac.nombre                         AS paciente,
               c.fecha                            AS fecha,
               c.costo                            AS costo,
               v.id                               AS id_veterinario,
               v.nombre + ' ' + v.apellido        AS veterinario
        ORDER BY c.costo ASC
    """)


# Q10 

def q10_pacientes_por_sucursal(sucursal: str):
    """
    Q10: Retorna todos los pacientes atendidos en una sucursal determinada,
    navegando la relación a través del veterinario.

    Args:
        sucursal: Nombre de la sucursal (ej: 'Palermo', 'Belgrano', 'Caballito').
    """
    return run_query("""
        MATCH (v:Veterinario {sucursal: $sucursal})-[:ATIENDE]->(c:Consulta)
        MATCH (pac:Paciente)-[:TIENE]->(c)
        MATCH (prop:Propietario)-[:TIENE]->(pac)
        RETURN DISTINCT
               pac.id                            AS id_paciente,
               pac.nombre                        AS paciente,
               pac.especie                       AS especie,
               prop.nombre + ' ' + prop.apellido  AS propietario,
               prop.telefono                     AS telefono
        ORDER BY pac.nombre
    """, {"sucursal": sucursal})


# Q11 

def q11_ingresos_por_veterinario_mes_actual():
    """
    Q11: Retorna los ingresos totales generados por todos los veterinarios
    en el mes actual.
    """
    hoy = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1).isoformat()
    fin_mes = hoy.isoformat()

    return run_query("""
        MATCH (v:Veterinario)
        OPTIONAL MATCH (v)-[:ATIENDE]->(c:Consulta)
        WHERE c.fecha >= $inicio AND c.fecha <= $fin
        RETURN v.id                               AS id_veterinario,
               v.nombre + ' ' + v.apellido        AS veterinario,
               v.sucursal                         AS sucursal,
               count(c)                           AS cantidad_consultas,
               coalesce(sum(c.costo), 0)          AS ingresos_totales
        ORDER BY ingresos_totales DESC
    """, {"inicio": inicio_mes, "fin": fin_mes})


# Q12

def q12_propietarios_sin_consultas_ultimo_anio():
    """
    Q12: Retorna los propietarios cuyos pacientes no tuvieron ninguna consulta
    registrada en el último año.
    """
    fecha_limite = (date.today() - timedelta(days=365)).isoformat()
    return run_query("""
        MATCH (prop:Propietario)-[:TIENE]->(pac:Paciente)
        WHERE NOT EXISTS {
            MATCH (pac)-[:TIENE]->(c:Consulta)
            WHERE c.fecha >= $fecha_limite
        }
        RETURN DISTINCT
               prop.id                            AS id_propietario,
               prop.nombre + ' ' + prop.apellido  AS propietario,
               prop.telefono                      AS telefono,
               collect({id_paciente: pac.id, paciente: pac.nombre}) AS mascotas
        ORDER BY propietario
    """, {"fecha_limite": fecha_limite})


# Q13 — ABM de propietarios

def q13_alta_propietario(datos: dict):
    """
    Q13 — Alta: Registra un nuevo propietario en el sistema.

    El ID se genera automáticamente con formato CXXX, por lo que no debe
    recibirse desde el input del usuario.

    Args:
        datos: Dict con campos nombre, apellido, dni, email, telefono,
               ciudad, provincia.
    """
    campos_obligatorios = ["nombre", "apellido", "dni", "email", "telefono", "ciudad", "provincia"]
    faltante = _validar_campos_requeridos(datos, campos_obligatorios)
    if faltante:
        return {
            "ok": False,
            "mensaje": f"Falta completar el campo '{faltante}'. Revisá los datos e intentá nuevamente.",
        }

    dni_existente = run_query(
        "MATCH (p:Propietario {dni: $dni}) RETURN p.id AS id, p.nombre AS nombre, p.apellido AS apellido",
        {"dni": str(datos["dni"]).strip()},
    )
    if dni_existente:
        propietario = dni_existente[0]
        return {
            "ok": False,
            "mensaje": (
                "Ya hay un propietario registrado con ese DNI: "
                f"{propietario['nombre']} {propietario['apellido']} ({propietario['id']})."
            ),
        }

    nuevo_id = _siguiente_id_neo4j("Propietario", "C")
    params = {
        "id": nuevo_id,
        "nombre": str(datos["nombre"]).strip(),
        "apellido": str(datos["apellido"]).strip(),
        "dni": str(datos["dni"]).strip(),
        "email": str(datos["email"]).strip(),
        "telefono": str(datos["telefono"]).strip(),
        "ciudad": str(datos["ciudad"]).strip(),
        "provincia": str(datos["provincia"]).strip(),
    }

    run_query("""
        CREATE (:Propietario {
            id:        $id,
            nombre:    $nombre,
            apellido:  $apellido,
            dni:       $dni,
            email:     $email,
            telefono:  $telefono,
            ciudad:    $ciudad,
            provincia: $provincia,
            activo:    true
        })
    """, params)

    return {
        "ok": True,
        "id_generado": nuevo_id,
        "mensaje": f"Propietario creado correctamente con ID {nuevo_id}: {params['nombre']} {params['apellido']}.",
    }


def q13_modificar_propietario(id_propietario: str, campos: dict):
    """
    Q13 — Modificación: Actualiza uno o más campos de un propietario existente.

    Args:
        id_propietario: ID del propietario a modificar.
        campos: Dict con los campos a actualizar (solo los que cambian).

    Ejemplo:
        q13_modificar_propietario('C001', {'email': 'nuevo@gmail.com', 'telefono': '1199999999'})
    """
    if not campos:
        return {"ok": False, "mensaje": "No se especificaron campos a modificar."}

    set_clause = ", ".join([f"p.{k} = ${k}" for k in campos.keys()])
    params = {"id": id_propietario, **campos}

    resultado = run_query(
        f"MATCH (p:Propietario {{id: $id}}) SET {set_clause} RETURN p.id AS id",
        params
    )
    if not resultado:
        return {"ok": False, "mensaje": f"No se encontró propietario con id '{id_propietario}'."}
    return {"ok": True, "mensaje": f"Propietario '{id_propietario}' actualizado correctamente."}


def q13_baja_logica_propietario(id_propietario: str):
    """
    Q13 — Baja lógica: Marca un propietario como inactivo sin eliminarlo del grafo.

    Args:
        id_propietario: ID del propietario a dar de baja.
    """
    resultado = run_query("""
        MATCH (p:Propietario {id: $id})
        SET p.activo = false
        RETURN p.id AS id
    """, {"id": id_propietario})

    if not resultado:
        return {"ok": False, "mensaje": f"No se encontró propietario con id '{id_propietario}'."}
    return {"ok": True, "mensaje": f"Propietario '{id_propietario}' dado de baja lógica correctamente."}


# Q14

def q14_registrar_consulta(datos: dict):
    """
    Q14: Registra una nueva consulta médica validando que el paciente
    y el veterinario existan en el sistema.

    El ID se genera automáticamente con formato CONXXX, por lo que no debe
    recibirse desde el input del usuario.

    Args:
        datos: Dict con campos id_paciente, id_vet, fecha, motivo,
               diagnostico, costo, estado.
    """
    campos_obligatorios = ["id_paciente", "id_vet", "fecha", "motivo", "diagnostico", "costo", "estado"]
    faltante = _validar_campos_requeridos(datos, campos_obligatorios)
    if faltante:
        return {
            "ok": False,
            "mensaje": f"Falta completar el campo '{faltante}'. Revisá los datos e intentá nuevamente.",
        }

    id_paciente = str(datos["id_paciente"]).strip().upper()
    id_vet = str(datos["id_vet"]).strip().upper()
    estado = _normalizar_estado_consulta(datos["estado"])

    if estado not in {"Cerrada", "Seguimiento"}:
        return {
            "ok": False,
            "mensaje": "El estado de la consulta debe ser 'Cerrada' o 'Seguimiento'.",
        }

    try:
        costo = float(datos["costo"])
    except (TypeError, ValueError):
        return {"ok": False, "mensaje": "El costo debe ser un número válido."}

    if costo < 0:
        return {"ok": False, "mensaje": "El costo no puede ser negativo."}

    paciente = run_query(
        "MATCH (p:Paciente {id: $id, activo: true}) RETURN p.nombre AS nombre",
        {"id": id_paciente},
    )
    if not paciente:
        return {
            "ok": False,
            "mensaje": f"No encontramos un paciente activo con ID {id_paciente}. Verificá el ID antes de registrar la consulta.",
        }

    veterinario = run_query(
        "MATCH (v:Veterinario {id: $id, activo: true}) RETURN v.nombre AS nombre, v.apellido AS apellido",
        {"id": id_vet},
    )
    if not veterinario:
        return {
            "ok": False,
            "mensaje": f"No encontramos un veterinario activo con ID {id_vet}. Verificá el ID antes de registrar la consulta.",
        }

    nuevo_id = _siguiente_id_neo4j("Consulta", "CON")

    run_query("""
        MATCH (pac:Paciente    {id: $id_paciente})
        MATCH (vet:Veterinario {id: $id_vet})
        CREATE (c:Consulta {
            id:          $id_consulta,
            fecha:       $fecha,
            motivo:      $motivo,
            diagnostico: $diagnostico,
            costo:       $costo,
            estado:      $estado
        })
        CREATE (pac)-[:TIENE]->(c)
        CREATE (vet)-[:ATIENDE]->(c)
    """, {
        "id_paciente": id_paciente,
        "id_vet": id_vet,
        "id_consulta": nuevo_id,
        "fecha": str(datos["fecha"]).strip(),
        "motivo": str(datos["motivo"]).strip(),
        "diagnostico": str(datos["diagnostico"]).strip(),
        "costo": costo,
        "estado": estado,
    })

    vet = veterinario[0]
    return {
        "ok": True,
        "id_generado": nuevo_id,
        "mensaje": (
            f"Consulta registrada correctamente con ID {nuevo_id}: "
            f"{paciente[0]['nombre']} con Dr/a. {vet['nombre']} {vet['apellido']} ({datos['fecha']})."
        ),
    }

