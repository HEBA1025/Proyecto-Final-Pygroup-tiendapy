from datetime import date
from pathlib import Path
from typing import Dict, Any
from tabulate import tabulate
from persistencia import RUTA_VENTAS, RUTA_INVENTARIO, guardar_inventario, registrar_venta_archivo
from validaciones import ReglaNegocioError

def crear_carrito() -> Dict[str, Dict[str, Any]]:
    return {}

def agregar_al_carrito(
    inventario: Dict[str, Dict[str, Any]],
    carrito: Dict[str, Dict[str, Any]],
    codigo: str,
    cantidad: int
) -> bool:
    codigo_limpio = codigo.strip().upper()

    if codigo_limpio not in inventario:
        raise ReglaNegocioError(f"El producto '{codigo_limpio}' no existe en el inventario.")

    if cantidad <= 0:
        raise ReglaNegocioError("La cantidad debe ser un numero entero mayor a cero.")

    producto = inventario[codigo_limpio]
    stock_disponible = producto["stock"]
    cantidad_actual = carrito.get(codigo_limpio, {}).get("cantidad", 0)
    cantidad_total = cantidad_actual + cantidad

    if cantidad_total > stock_disponible:
        raise ReglaNegocioError(
            f"Stock insuficiente para '{producto['nombre']}'. Disponible: {stock_disponible}, solicitado: {cantidad_total}."
        )

    subtotal_item = round(cantidad_total * producto["precio"], 2)

    carrito[codigo_limpio] = {
        "codigo": codigo_limpio,
        "nombre": producto["nombre"],
        "precio": producto["precio"],
        "cantidad": cantidad_total,
        "subtotal": subtotal_item
    }
    return True

def calcular_totales(carrito: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    subtotal = sum(item["subtotal"] for item in carrito.values())
    subtotal = round(subtotal, 2)

    porcentaje_descuento = 0.0
    if subtotal >= 100000.0:
        porcentaje_descuento = 0.10
    elif subtotal >= 50000.0:
        porcentaje_descuento = 0.05

    descuento = round(subtotal * porcentaje_descuento, 2)
    total = round(subtotal - descuento, 2)

    return {
        "subtotal": subtotal,
        "porcentaje_descuento": porcentaje_descuento * 100,
        "descuento": descuento,
        "total": total
    }

def formatear_detalle_venta(carrito: Dict[str, Dict[str, Any]], totales: Dict[str, float]) -> str:
    filas = []
    for item in carrito.values():
        filas.append([
            item["codigo"],
            item["nombre"],
            f"${item['precio']:,.1f}",
            item["cantidad"],
            f"${item['subtotal']:,.1f}"
        ])

    encabezados = ["Codigo", "Producto", "Precio Unit.", "Cant.", "Subtotal"]
    tabla = tabulate(filas, headers=encabezados, tablefmt="rounded_grid")

    resumen = (
        f"\n{tabla}\n"
        f"  Subtotal:         ${totales['subtotal']:>12,.1f} COP\n"
        f"  Descuento ({int(totales['porcentaje_descuento'])}%): -${totales['descuento']:>12,.1f} COP\n"
        f"  TOTAL A PAGAR:    ${totales['total']:>12,.1f} COP\n"
    )
    return resumen

def procesar_pago(total: float, monto_recibido: float) -> float:
    if monto_recibido < total:
        faltante = round(total - monto_recibido, 2)
        raise ReglaNegocioError(f"Pago insuficiente. Faltan ${faltante:,.1f} COP.")
    return round(monto_recibido - total, 2)

def confirmar_venta(
    inventario: Dict[str, Dict[str, Any]],
    carrito: Dict[str, Dict[str, Any]],
    total: float,
    ruta_ventas: Path | str = RUTA_VENTAS,
    ruta_inventario: Path | str = RUTA_INVENTARIO
) -> bool:
    if not carrito:
        raise ReglaNegocioError("El carrito esta vacio.")

    for cod, item in carrito.items():
        if item["cantidad"] > inventario[cod]["stock"]:
            raise ReglaNegocioError(
                f"No hay suficiente stock para confirmar la venta de '{inventario[cod]['nombre']}'."
            )

    for cod, item in carrito.items():
        inventario[cod]["stock"] -= item["cantidad"]

    if not guardar_inventario(inventario, ruta_inventario):
        raise ReglaNegocioError("No se pudo persistir el inventario actualizado.")

    detalle = ";".join(f"{item['codigo']}:{item['cantidad']}" for item in carrito.values())
    fecha_hoy = date.today().isoformat()
    linea_registro = f"{fecha_hoy}|{total:.1f}|{detalle}\n"

    if not registrar_venta_archivo(linea_registro, ruta_ventas):
        raise ReglaNegocioError("No se pudo registrar la venta en el archivo de ventas.")

    return True