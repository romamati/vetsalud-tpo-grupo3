"""
mongodb_db/connection.py
Módulo de conexión a MongoDB.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client() -> MongoClient:
    """
    Devuelve una instancia singleton del cliente MongoDB.
    Reutiliza la conexión si ya fue establecida.
    """
    global _client
    if _client is None:
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        _client = MongoClient(uri)
        # Verificar que la conexión sea exitosa
        try:
            _client.admin.command("ping")
            print("[MongoDB] Conexión establecida correctamente.")
        except ConnectionFailure as e:
            print(f"[MongoDB] ERROR al conectar: {e}")
            raise
    return _client


def get_db():
    """
    Devuelve la base de datos VetSalud de MongoDB.
    """
    db_name = os.getenv("MONGO_DB", "vetsalud")
    return get_client()[db_name]


def close_connection():
    """
    Cierra la conexión a MongoDB.
    """
    global _client
    if _client is not None:
        _client.close()
        _client = None
        print("[MongoDB] Conexión cerrada.")


if __name__ == "__main__":
    # Test rápido de conexión
    db = get_db()
    print(f"[MongoDB] Base de datos activa: {db.name}")
    print(f"[MongoDB] Colecciones disponibles: {db.list_collection_names()}")
    close_connection()