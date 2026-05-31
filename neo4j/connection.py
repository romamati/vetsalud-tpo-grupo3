"""
neo4j/connection.py
Módulo de conexión a Neo4j.
"""

import os
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from dotenv import load_dotenv

load_dotenv()

_driver = None


def get_driver():
    """
    Devuelve una instancia singleton del driver de Neo4j.
    Reutiliza la conexión si ya fue establecida.
    """
    global _driver
    if _driver is None:
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")
        try:
            _driver = GraphDatabase.driver(uri, auth=(user, password))
            _driver.verify_connectivity()
            print("[Neo4j] Conexión establecida correctamente.")
        except ServiceUnavailable as e:
            print(f"[Neo4j] ERROR al conectar: {e}")
            raise
    return _driver


def run_query(query: str, parameters: dict = None):
    """
    Ejecuta una query Cypher y devuelve los resultados como lista de diccionarios.

    Args:
        query: Query Cypher a ejecutar.
        parameters: Parámetros opcionales para la query.

    Returns:
        Lista de registros como diccionarios.
    """
    driver = get_driver()
    parameters = parameters or {}
    with driver.session() as session:
        result = session.run(query, parameters)
        return [record.data() for record in result]


def close_connection():
    """
    Cierra la conexión a Neo4j.
    """
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
        print("[Neo4j] Conexión cerrada.")


if __name__ == "__main__":
    # Test rápido de conexión
    result = run_query("RETURN 'Conexión Neo4j OK' AS mensaje")
    print(f"[Neo4j] {result[0]['mensaje']}")
    close_connection()