"""
queries/mongodb_queries.py
Consultas sobre MongoDB.

Q8  — Stock con menos de 50 unidades y su proveedor
Q15 — Actualización masiva del stock tras una consulta
"""

from mongodb_db.connection import get_db


# Q8

def q8_stock_bajo(umbral: int = 50):
    """
    Q8: Productos con menos de `umbral` unidades en stock, ordenados por unidades.

    Returns:
        Lista de dicts con nombre, categoria, unidades y proveedor.

    Ejemplo de resultado:
        [
          {'nombre': 'Ketamina 10%', 'categoria': 'Anestésico', 'unidades': 25, 'proveedor': 'MediAnimal'},
          {'nombre': 'Propofol 10mg/ml', 'categoria': 'Anestésico', 'unidades': 20, 'proveedor': 'MediAnimal'},
          ...
        ]
    """
    db = get_db()
    resultados = db["stock_farmaceutico"].find(
        {"unidades": {"$lt": umbral}},
        {"_id": 1, "nombre": 1, "categoria": 1, "unidades": 1, "proveedor": 1}
    ).sort("unidades", 1)

    return list(resultados)


# Q15 

def q15_actualizar_stock(id_producto: str, cantidad_usada: int):
    """
    Q15: Decrementa las unidades de un producto tras su uso en una consulta.
    Valida que el producto exista y que haya stock suficiente.

    Args:
        id_producto:   ID del producto a actualizar (ej: 'PRD001').
        cantidad_usada: Cantidad de unidades a descontar.

    Returns:
        Dict con resultado de la operación.

    Ejemplo de resultado (éxito):
        {'ok': True, 'mensaje': "Stock de 'Amoxicilina 250mg' actualizado: 120 → 118 unidades."}

    Ejemplo de resultado (sin stock):
        {'ok': False, 'mensaje': "Stock insuficiente: solo 2 unidades disponibles de 'Amoxicilina 250mg'."}
    """
    db = get_db()
    col = db["stock_farmaceutico"]

    producto = col.find_one({"_id": id_producto})
    if not producto:
        return {"ok": False, "mensaje": f"Producto '{id_producto}' no encontrado."}

    if producto["unidades"] < cantidad_usada:
        return {
            "ok": False,
            "mensaje": (
                f"Stock insuficiente: solo {producto['unidades']} unidades "
                f"disponibles de '{producto['nombre']}'."
            ),
        }

    col.update_one(
        {"_id": id_producto},
        {"$inc": {"unidades": -cantidad_usada}}
    )

    unidades_nuevas = producto["unidades"] - cantidad_usada
    return {
        "ok": True,
        "mensaje": (
            f"Stock de '{producto['nombre']}' actualizado: "
            f"{producto['unidades']} → {unidades_nuevas} unidades."
        ),
    }


# Ejecución directa (demo)

if __name__ == "__main__":
    print("\n── Q8: Stock bajo (< 50 unidades) ──")
    for p in q8_stock_bajo():
        print(f"  {p['nombre']:30s} | {p['unidades']:>3} u. | {p['proveedor']}")

    print("\n── Q15: Actualizar stock ──")
    resultado = q15_actualizar_stock("PRD001", 2)
    print(f"  {resultado['mensaje']}")