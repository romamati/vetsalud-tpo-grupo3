"""
mongodb/load_data.py
Carga los datasets CSV en MongoDB.
Solo el stock farmacéutico vive en MongoDB como colección principal.
Las demás colecciones se cargan como referencia auxiliar para consultas híbridas.
"""

import os
import pandas as pd
from mongodb_db.connection import get_db, close_connection

# Ruta base a los CSVs (relativa a la raíz del proyecto)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def limpiar_colecciones(db):
    """Elimina todos los documentos de las colecciones antes de recargar."""
    colecciones = ["stock_farmaceutico"]
    for col in colecciones:
        resultado = db[col].delete_many({})
        print(f"  [limpieza] '{col}': {resultado.deleted_count} documentos eliminados.")


def cargar_stock(db):
    """
    Carga el inventario farmacéutico en MongoDB.
    Paradigma documental: cada producto es un documento independiente
    con todos sus atributos embebidos.
    """
    ruta = os.path.join(DATA_DIR, "stock_farmaceutico.csv")
    df = pd.read_csv(ruta)

    documentos = []
    for _, fila in df.iterrows():
        documentos.append({
            "_id":         fila["id_producto"],
            "nombre":      fila["nombre"],
            "categoria":   fila["categoria"],
            "unidades":    int(fila["unidades"]),
            "precio_unit": float(fila["precio_unit"]),
            "vencimiento": fila["vencimiento"],
            "proveedor":   fila["proveedor"],
        })

    resultado = db["stock_farmaceutico"].insert_many(documentos)
    print(f"  [stock_farmaceutico] {len(resultado.inserted_ids)} documentos insertados.")


def main():
    print("\n📦 Iniciando carga de datos en MongoDB...\n")
    db = get_db()

    print("🧹 Limpiando colecciones existentes...")
    limpiar_colecciones(db)

    print("\n📥 Insertando datos...")
    cargar_stock(db)

    print("\n✅ Carga en MongoDB finalizada.")
    print(f"   Colecciones disponibles: {db.list_collection_names()}")
    close_connection()


if __name__ == "__main__":
    main()