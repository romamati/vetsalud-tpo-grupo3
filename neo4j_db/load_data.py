"""
neo4j_db/load_data.py
Carga los datasets CSV en Neo4j como nodos y relaciones.

Nodos: Propietario, Paciente, Veterinario, Consulta, Vacunacion
Relaciones:
  (Propietario)-[:TIENE]->(Paciente)
  (Paciente)-[:TIENE]->(Consulta)
  (Veterinario)-[:ATIENDE]->(Consulta)
  (Paciente)-[:RECIBE]->(Vacunacion)
  (Veterinario)-[:APLICA]->(Vacunacion)
"""

import os
import pandas as pd
from neo4j_db.connection import run_query, close_connection

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def limpiar_grafo():
    """Elimina todos los nodos y relaciones existentes."""
    run_query("MATCH (n) DETACH DELETE n")
    print("  [limpieza] Grafo vaciado.")


# Carga de nodos

def cargar_propietarios():
    df = pd.read_csv(os.path.join(DATA_DIR, "propietarios.csv"))
    for _, r in df.iterrows():
        run_query("""
            CREATE (:Propietario {
                id:         $id,
                nombre:     $nombre,
                apellido:   $apellido,
                dni:        $dni,
                email:      $email,
                telefono:   $telefono,
                ciudad:     $ciudad,
                provincia:  $provincia,
                activo:     true
            })
        """, {
            "id": r["id_propietario"], "nombre": r["nombre"],
            "apellido": r["apellido"], "dni": str(r["dni"]),
            "email": r["email"], "telefono": str(r["telefono"]),
            "ciudad": r["ciudad"], "provincia": r["provincia"],
        })
    print(f"  [Propietario] {len(df)} nodos creados.")


def cargar_pacientes():
    df = pd.read_csv(os.path.join(DATA_DIR, "pacientes.csv"))
    for _, r in df.iterrows():
        run_query("""
            CREATE (:Paciente {
                id:         $id,
                nombre:     $nombre,
                especie:    $especie,
                raza:       $raza,
                fecha_nac:  $fecha_nac,
                activo:     $activo
            })
        """, {
            "id": r["id_paciente"], "nombre": r["nombre"],
            "especie": r["especie"], "raza": r["raza"],
            "fecha_nac": r["fecha_nac"],
            "activo": str(r["activo"]).strip().lower() == "true",
        })
    print(f"  [Paciente] {len(df)} nodos creados.")


def cargar_veterinarios():
    df = pd.read_csv(os.path.join(DATA_DIR, "veterinarios.csv"))
    for _, r in df.iterrows():
        run_query("""
            CREATE (:Veterinario {
                id:           $id,
                nombre:       $nombre,
                apellido:     $apellido,
                matricula:    $matricula,
                especialidad: $especialidad,
                sucursal:     $sucursal,
                activo:       $activo
            })
        """, {
            "id": r["id_vet"], "nombre": r["nombre"],
            "apellido": r["apellido"], "matricula": r["matricula"],
            "especialidad": r["especialidad"], "sucursal": r["sucursal"],
            "activo": str(r["activo"]).strip().lower() == "true",
        })
    print(f"  [Veterinario] {len(df)} nodos creados.")


def cargar_consultas():
    df = pd.read_csv(os.path.join(DATA_DIR, "consultas.csv"))
    for _, r in df.iterrows():
        run_query("""
            CREATE (:Consulta {
                id:          $id,
                fecha:       $fecha,
                motivo:      $motivo,
                diagnostico: $diagnostico,
                costo:       $costo,
                estado:      $estado
            })
        """, {
            "id": r["id_consulta"], "fecha": r["fecha"],
            "motivo": r["motivo"], "diagnostico": r["diagnostico"],
            "costo": float(r["costo"]), "estado": r["estado"],
        })
    print(f"  [Consulta] {len(df)} nodos creados.")


def cargar_vacunaciones():
    df = pd.read_csv(os.path.join(DATA_DIR, "vacunaciones.csv"))
    for _, r in df.iterrows():
        run_query("""
            CREATE (:Vacunacion {
                id:              $id,
                fecha_aplicacion: $fecha_aplicacion,
                nombre_vacuna:   $nombre_vacuna,
                proxima_dosis:   $proxima_dosis
            })
        """, {
            "id": r["id_vacuna"],
            "fecha_aplicacion": r["fecha_aplicacion"],
            "nombre_vacuna": r["nombre_vacuna"],
            "proxima_dosis": r["proxima_dosis"],
        })
    print(f"  [Vacunacion] {len(df)} nodos creados.")


# Carga de relaciones

def crear_relacion_propietario_paciente():
    df = pd.read_csv(os.path.join(DATA_DIR, "pacientes.csv"))
    for _, r in df.iterrows():
        run_query("""
            MATCH (p:Propietario {id: $id_prop})
            MATCH (pac:Paciente  {id: $id_pac})
            CREATE (p)-[:TIENE]->(pac)
        """, {"id_prop": r["id_propietario"], "id_pac": r["id_paciente"]})
    print(f"  [TIENE] {len(df)} relaciones Propietario→Paciente creadas.")


def crear_relacion_paciente_consulta():
    df = pd.read_csv(os.path.join(DATA_DIR, "consultas.csv"))
    for _, r in df.iterrows():
        run_query("""
            MATCH (pac:Paciente {id: $id_pac})
            MATCH (c:Consulta   {id: $id_con})
            CREATE (pac)-[:TIENE]->(c)
        """, {"id_pac": r["id_paciente"], "id_con": r["id_consulta"]})
    print(f"  [TIENE] {len(df)} relaciones Paciente→Consulta creadas.")


def crear_relacion_veterinario_consulta():
    df = pd.read_csv(os.path.join(DATA_DIR, "consultas.csv"))
    for _, r in df.iterrows():
        run_query("""
            MATCH (v:Veterinario {id: $id_vet})
            MATCH (c:Consulta    {id: $id_con})
            CREATE (v)-[:ATIENDE]->(c)
        """, {"id_vet": r["id_vet"], "id_con": r["id_consulta"]})
    print(f"  [ATIENDE] {len(df)} relaciones Veterinario→Consulta creadas.")


def crear_relacion_paciente_vacunacion():
    df = pd.read_csv(os.path.join(DATA_DIR, "vacunaciones.csv"))
    for _, r in df.iterrows():
        run_query("""
            MATCH (pac:Paciente  {id: $id_pac})
            MATCH (v:Vacunacion  {id: $id_vac})
            CREATE (pac)-[:RECIBE]->(v)
        """, {"id_pac": r["id_paciente"], "id_vac": r["id_vacuna"]})
    print(f"  [RECIBE] {len(df)} relaciones Paciente→Vacunacion creadas.")


def crear_relacion_veterinario_vacunacion():
    df = pd.read_csv(os.path.join(DATA_DIR, "vacunaciones.csv"))
    for _, r in df.iterrows():
        run_query("""
            MATCH (v:Veterinario {id: $id_vet})
            MATCH (vac:Vacunacion {id: $id_vac})
            CREATE (v)-[:APLICA]->(vac)
        """, {"id_vet": r["id_vet"], "id_vac": r["id_vacuna"]})
    print(f"  [APLICA] {len(df)} relaciones Veterinario→Vacunacion creadas.")


# Índices para mejorar performance

def crear_indices():
    indices = [
        "CREATE INDEX IF NOT EXISTS FOR (n:Propietario) ON (n.id)",
        "CREATE INDEX IF NOT EXISTS FOR (n:Paciente)    ON (n.id)",
        "CREATE INDEX IF NOT EXISTS FOR (n:Veterinario) ON (n.id)",
        "CREATE INDEX IF NOT EXISTS FOR (n:Consulta)    ON (n.id)",
        "CREATE INDEX IF NOT EXISTS FOR (n:Vacunacion)  ON (n.id)",
    ]
    for q in indices:
        run_query(q)
    print(f"  [índices] {len(indices)} índices creados.")


# Main

def main():
    print("\n🔵 Iniciando carga de datos en Neo4j...\n")

    print("🧹 Limpiando grafo existente...")
    limpiar_grafo()

    print("\n📥 Creando nodos...")
    cargar_propietarios()
    cargar_pacientes()
    cargar_veterinarios()
    cargar_consultas()
    cargar_vacunaciones()

    print("\n🔗 Creando relaciones...")
    crear_relacion_propietario_paciente()
    crear_relacion_paciente_consulta()
    crear_relacion_veterinario_consulta()
    crear_relacion_paciente_vacunacion()
    crear_relacion_veterinario_vacunacion()

    print("\n⚡ Creando índices...")
    crear_indices()

    resumen = run_query("""
        MATCH (n) RETURN labels(n)[0] AS tipo, count(n) AS cantidad
        ORDER BY tipo
    """)
    print("\n✅ Carga en Neo4j finalizada. Resumen de nodos:")
    for r in resumen:
        print(f"   {r['tipo']:15s} → {r['cantidad']} nodos")

    close_connection()


if __name__ == "__main__":
    main()