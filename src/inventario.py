"""
Modulo de gestion de inventario para TiendaPy.
Implementa operaciones CRUD y busquedas sobre los productos.
Cumple con CF-03, CF-04, CF-05, CR-02 y CR-06.
"""

from typing import Dict, Any, List, Optional


def agregar_producto(
        inventario: Dict[str, Dict[str, Any]],
        codigo: str,
        nombre: str,
        categoria: str,
        precio: float,
        stock: int,
        stock_minimo: int,
        proveedor: str
) -> bool:
    """
    Registra un producto nuevo en el inventario (CF-03).
    Rechaza codigos duplicados y valores numericos no permitidos (CR-02).
    """
    codigo_limpio = codigo.strip().upper()

    # Validacion de codigo duplicado (CF-03)
    if codigo_limpio in inventario:
        print(f"[ERROR] Ya existe un producto con el codigo '{codigo_limpio}'.")
        return False

    # Validaciones de reglas de negocio (CR-02)
    if precio <= 0:
        print("[ERROR] El precio debe ser un valor mayor a cero.")
        return False
    if stock < 0 or stock_minimo < 0:
        print("[ERROR] El stock y el stock minimo no pueden ser negativos.")
        return False

    inventario[codigo_limpio] = {
        "codigo": codigo_limpio,
        "nombre": nombre.strip(),
        "categoria": categoria.strip(),
        "precio": float(precio),
        "stock": int(stock),
        "stock_minimo": int(stock_minimo),
        "proveedor": proveedor.strip()
    }
    print(f"[EXITO] Producto '{nombre}' ({codigo_limpio}) registrado correctamente.")
    return True


def consultar_por_codigo(
        inventario: Dict[str, Dict[str, Any]],
        codigo: str
) -> Optional[Dict[str, Any]]:
    """
    Consulta un producto por su codigo unico (CF-04).
    Si no existe, informa de forma controlada sin fallar.
    """
    codigo_limpio = codigo.strip().upper()
    producto = inventario.get(codigo_limpio)

    if not producto:
        print(f"[INFO] No se encontro ningun producto con el codigo '{codigo_limpio}'.")
        return None

    return producto


def buscar_por_categoria(
        inventario: Dict[str, Dict[str, Any]],
        categoria: str
) -> List[Dict[str, Any]]:
    """
    Filtra y retorna productos pertenecientes a una categoria (CF-04).
    Busqueda no sensible a mayusculas/minusculas.
    """
    categoria_busqueda = categoria.strip().lower()
    coincidencias = [
        prod for prod in inventario.values()
        if prod["categoria"].lower() == categoria_busqueda
    ]

    if not coincidencias:
        print(f"[INFO] No hay productos registrados en la categoria '{categoria}'.")
    return coincidencias


def modificar_producto(
        inventario: Dict[str, Dict[str, Any]],
        codigo: str,
        nuevo_precio: Optional[float] = None,
        nuevo_stock: Optional[int] = None
) -> bool:
    """
    Modifica el precio y/o stock de un producto existente (CF-05).
    Valida que los nuevos valores sean validos (CR-02).
    """
    codigo_limpio = codigo.strip().upper()
    if codigo_limpio not in inventario:
        print(f"[ERROR] No se puede modificar: no existe el producto '{codigo_limpio}'.")
        return False

    if nuevo_precio is not None:
        if nuevo_precio <= 0:
            print("[ERROR] El nuevo precio debe ser mayor a cero.")
            return False
        inventario[codigo_limpio]["precio"] = float(nuevo_precio)

    if nuevo_stock is not None:
        if nuevo_stock < 0:
            print("[ERROR] El stock no puede ser negativo.")
            return False
        inventario[codigo_limpio]["stock"] = int(nuevo_stock)

    print(f"[EXITO] Producto '{codigo_limpio}' modificado con exito.")
    return True


def eliminar_producto(
        inventario: Dict[str, Dict[str, Any]],
        codigo: str
) -> bool:
    """
    Elimina un producto del inventario (CF-05).
    """
    codigo_limpio = codigo.strip().upper()
    if codigo_limpio not in inventario:
        print(f"[ERROR] No se puede eliminar: el producto '{codigo_limpio}' no existe.")
        return False

    eliminado = inventario.pop(codigo_limpio)
    print(f"[EXITO] Producto '{eliminado['nombre']}' ({codigo_limpio}) eliminado del inventario.")
    return True


if __name__ == "__main__":
    from persistencia import cargar_inventario

    print("--- PROBANDO MODULO DE INVENTARIO (src/inventario.py) ---")
    inv = cargar_inventario()

    # 1. Probar agregar producto (CF-03)
    print("\n1. Agregar nuevo producto:")
    agregar_producto(inv, "PAN001", "Pan Tajado", "Abarrotes", 3500.0, 20, 5, "Bimbo")

    # 1.1 Probar rechazo de duplicado (CF-03)
    print("\n1.1 Intento de duplicar codigo:")
    agregar_producto(inv, "PAN001", "Otro Pan", "Abarrotes", 4000.0, 10, 5, "Bimbo")

    # 2. Consultar por codigo (CF-04)
    print("\n2. Consulta por codigo:")
    prod = consultar_por_codigo(inv, "LAC001")
    print(f"Encontrado: {prod}")
    consultar_por_codigo(inv, "XYZ999")  # Caso no existente

    # 3. Buscar por categoria (CF-04)
    print("\n3. Filtrar por categoria 'Bebidas':")
    bebidas = buscar_por_categoria(inv, "Bebidas")
    for b in bebidas:
        print(f"  - {b['nombre']} | ${b['precio']} | Stock: {b['stock']}")

    # 4. Modificar producto (CF-05)
    print("\n4. Modificar precio y stock:")
    modificar_producto(inv, "LAC001", nuevo_precio=4500.0, nuevo_stock=40)
    print(f"Actualizado: {inv['LAC001']}")

    # 5. Eliminar producto (CF-05)
    print("\n5. Eliminar producto:")
    eliminar_producto(inv, "PAN001")
    eliminar_producto(inv, "NO_EXISTE")