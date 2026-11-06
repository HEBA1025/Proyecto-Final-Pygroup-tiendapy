"""
Modulo de ventas y facturacion para TiendaPy.
Maneja carrito de compras, descuentos, calculo de cambio y registro de transacciones.
Cumple con CF-06, CF-07, CF-08, CF-09, CF-10, CR-02 y CR-05.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Any, Tuple
from tabulate import tabulate
from persistencia import BASE_DIR, RUTA_VENTAS, RUTA_INVENTARIO, guardar_inventario


def crear_carrito() -> Dict[str, Dict[str, Any]]:
    """
    Inicializa un carrito de compras vacio indexado por codigo de producto.
    """
    return {}


def agregar_al_carrito(
        inventario: Dict[str, Dict[str, Any]],
        carrito: Dict[str, Dict[str, Any]],
        codigo: str,
        cantidad: int
) -> bool:
    """
    Agrega un producto al carrito validando stock disponible (CF-09, CR-02).
    """
    codigo_limpio = codigo.strip().upper()

    if codigo_limpio not in inventario:
        print(f"[ERROR] El producto con codigo '{codigo_limpio}' no existe en el inventario.")
        return False

    if cantidad <= 0:
        print("[ERROR] La cantidad a vender debe ser un entero positivo.")
        return False

    producto = inventario[codigo_limpio]
    stock_disponible = producto["stock"]
    cantidad_previa = carrito.get(codigo_limpio, {}).get("cantidad", 0)
    cantidad_total = cantidad_previa + cantidad

    # CF-09: Rechazar si supera el stock disponible
    if cantidad_total > stock_disponible:
        print(f"[RECHAZADO] Stock insuficiente para '{producto['nombre']}'. Disponible: {stock_disponible}, en carrito: {cantidad_total}.")
        return False

    subtotal_item = round(cantidad_total * producto["precio"], 2)

    carrito[codigo_limpio] = {
        "codigo": codigo_limpio,
        "nombre": producto["nombre"],
        "precio": producto["precio"],
        "cantidad": cantidad_total,
        "subtotal": subtotal_item
    }
    print(f"[OK] '{producto['nombre']}' x{cantidad} agregado al carrito.")
    return True


def calcular_totales(carrito: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    """
    Calcula subtotal, porcentaje, descuento y total a pagar (CF-07).
    Reglas de negocio 3.3:
      - Subtotal >= $50.000 COP -> 5% de descuento.
      - Subtotal >= $100.000 COP -> 10% de descuento.
    """
    subtotal = sum(item["subtotal"] for item in carrito.values())
    subtotal = round(subtotal, 2)

    porcentaje_descuento = 0.0
    if subtotal >= 100000.0:
        porcentaje_descuento = 0.10
    elif subtotal >= 50000.0:
        porcentaje_descuento = 0.05

    valor_descuento = round(subtotal * porcentaje_descuento, 2)
    total_a_pagar = round(subtotal - valor_descuento, 2)

    return {
        "subtotal": subtotal,
        "porcentaje_descuento": porcentaje_descuento * 100,
        "descuento": valor_descuento,
        "total": total_a_pagar
    }


def formatear_detalle_venta(carrito: Dict[str, Dict[str, Any]], totales: Dict[str, float]) -> str:
    """
    Genera el desglose formateado del carrito usando tabulate (CF-06).
    """
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


def procesar_pago(total: float, monto_recibido: float) -> Tuple[bool, float]:
    """
    Valida que el pago cubra el total y calcula el cambio (CF-08).
    """
    if monto_recibido < total:
        faltante = round(total - monto_recibido, 2)
        print(f"[PAGO INSUFICIENTE] Faltan ${faltante:,.1f} COP para cubrir el total.")
        return False, 0.0

    cambio = round(monto_recibido - total, 2)
    return True, cambio


def confirmar_venta(
        inventario: Dict[str, Dict[str, Any]],
        carrito: Dict[str, Dict[str, Any]],
        total: float,
        ruta_ventas: Path | str = RUTA_VENTAS,
        ruta_inventario: Path | str = RUTA_INVENTARIO
) -> bool:
    """
    Confirma la venta:
    1. Descuenta las unidades vendidas del stock en memoria.
    2. Actualiza 'data/inventario.txt' con el nuevo stock (CF-10, CF-13, CR-05).
    3. Registra la venta al final de 'data/ventas.txt' (CF-10, Seccion 3.4).
    """
    if not carrito:
        print("[ERROR] El carrito esta vacio.")
        return False

    # 1. Descontar stock en memoria
    for cod, item in carrito.items():
        inventario[cod]["stock"] -= item["cantidad"]

    # 2. Persistir inventario actualizado en data/inventario.txt
    if not guardar_inventario(inventario, ruta_inventario):
        print("[ERROR] No se pudo actualizar el stock en inventario.txt.")
        return False

    # 3. Formatear linea de venta: fecha|total|codigo:cantidad;codigo:cantidad
    detalle_codigos = ";".join(f"{item['codigo']}:{item['cantidad']}" for item in carrito.values())
    fecha_hoy = date.today().isoformat()
    linea_venta = f"{fecha_hoy}|{total:.1f}|{detalle_codigos}\n"

    # 4. Guardar al final de ventas.txt (modo append 'a' con context manager, CR-05)
    ruta_v = Path(ruta_ventas)
    ruta_v.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(ruta_v, mode="a", encoding="utf-8") as f:
            f.write(linea_venta)
        print("[EXITO] Venta registrada en 'data/ventas.txt' e inventario actualizado en disco.")
        return True
    except OSError as e:
        print(f"[ERROR] Error al escribir en '{ruta_v}': {e}")
        return False


if __name__ == "__main__":
    from persistencia import cargar_inventario

    print("--- PRUEBA INTEGRAL DE PERSISTENCIA DE VENTAS (src/ventas.py) ---")
    inv = cargar_inventario()
    cart = crear_carrito()

    # 1. Agregar productos al carrito
    print("\n1. Cargando productos al carrito:")
    agregar_al_carrito(inv, cart, "LAC001", 2)
    agregar_al_carrito(inv, cart, "BEB003", 1)

    # 2. Calcular totales y mostrar detalle
    totales = calcular_totales(cart)
    print(formatear_detalle_venta(cart, totales))

    # 3. Probar rechazo de pago insuficiente (CF-08)
    print("3. Validacion de pago insuficiente:")
    pago_ok, _ = procesar_pago(totales["total"], 10000.0)

    # 4. Probar pago valido y calculo de cambio (CF-08)
    print("\n4. Pago valido con billete de $20.000:")
    pago_ok, cambio = procesar_pago(totales["total"], 20000.0)
    if pago_ok:
        print(f"[PAGO RECIBIDO] Cambio a entregar: ${cambio:,.1f} COP")

    # 5. Confirmar venta y verificar persistencia en ambos archivos (CF-10)
    print("\n5. Confirmando venta y persistiendo en disco:")
    stock_previo_lac = inv["LAC001"]["stock"]
    confirmar_venta(inv, cart, totales["total"])
    print(f"Stock LAC001 en memoria: {stock_previo_lac} -> {inv['LAC001']['stock']}")