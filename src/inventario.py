from typing import Dict, Any, List, Optional
from validaciones import ReglaNegocioError

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
    codigo_limpio = codigo.strip().upper()

    if codigo_limpio in inventario:
        raise ReglaNegocioError(f"Ya existe un producto con el codigo '{codigo_limpio}'.")

    if precio <= 0:
        raise ReglaNegocioError("El precio debe ser un valor mayor a cero.")

    if stock <= 0:
        raise ReglaNegocioError("El stock inicial debe ser mayor a cero.")

    if stock_minimo < 0:
        raise ReglaNegocioError("El stock minimo no puede ser negativo.")

    inventario[codigo_limpio] = {
        "codigo": codigo_limpio,
        "nombre": nombre.strip(),
        "categoria": categoria.strip(),
        "precio": float(precio),
        "stock": int(stock),
        "stock_minimo": int(stock_minimo),
        "proveedor": proveedor.strip()
    }
    return True

def consultar_por_codigo(
    inventario: Dict[str, Dict[str, Any]],
    codigo: str
) -> Optional[Dict[str, Any]]:
    codigo_limpio = codigo.strip().upper()
    return inventario.get(codigo_limpio)

def buscar_por_categoria(
    inventario: Dict[str, Dict[str, Any]],
    categoria: str
) -> List[Dict[str, Any]]:
    cat_busqueda = categoria.strip().lower()
    return [
        prod for prod in inventario.values()
        if prod["categoria"].strip().lower() == cat_busqueda
    ]

def modificar_producto(
    inventario: Dict[str, Dict[str, Any]],
    codigo: str,
    nuevo_precio: Optional[float] = None,
    nuevo_stock: Optional[int] = None
) -> bool:
    codigo_limpio = codigo.strip().upper()
    if codigo_limpio not in inventario:
        raise ReglaNegocioError(f"No existe el producto con codigo '{codigo_limpio}'.")

    if nuevo_precio is not None:
        if nuevo_precio <= 0:
            raise ReglaNegocioError("El precio debe ser un valor mayor a cero.")
        inventario[codigo_limpio]["precio"] = float(nuevo_precio)

    if nuevo_stock is not None:
        if nuevo_stock <= 0:
            raise ReglaNegocioError("El stock debe ser un valor mayor a cero.")
        inventario[codigo_limpio]["stock"] = int(nuevo_stock)

    return True

def eliminar_producto(
    inventario: Dict[str, Dict[str, Any]],
    codigo: str
) -> Dict[str, Any]:
    codigo_limpio = codigo.strip().upper()
    if codigo_limpio not in inventario:
        raise ReglaNegocioError(f"El producto con codigo '{codigo_limpio}' no existe.")
    return inventario.pop(codigo_limpio)