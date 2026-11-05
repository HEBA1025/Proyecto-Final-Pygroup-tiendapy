"""
Modulo de ventas y facturacion para TiendaPy.
Maneja carrito de compras, descuentos, calculo de cambio y registro de transacciones.
Cumple con CF-06, CF-07, CF-08, CF-09, CF-10, CR-02 y CR-05.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Any, List, Tuple
from tabulate import tabulate
from persistencia import BASE_DIR, RUTA_VENTAS


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

    # CF-09: Control estricto de stock
    if cantidad_total > stock_disponible:
        print(f"[RECHAZADO] Stock insuficiente para '{producto['nombre']}'. Disponible: {stock_disponible}, solicitado: {cantidad_total}.")
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
    Calcula subtotal, porcentaje y valor de descuento y total a pagar (CF-07).
    Reglas de negocio:
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
    Genera una representacion visual en tabla de la venta usando tabulate (CF-06).
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
    Valida que el pago sea suficiente y calcula el cambio (CF-08).
    """
    if monto_recibido < total:
        faltante = round(total - monto_recibido, 2)
        print(f"[PAGO INSUFICIENTE] Faltan ${faltante:,.1f} COP para completar el total.")
        return False, 0.0

    cambio = round(monto_recibido - total, 2)
    return True, cambio


def confirmar_venta(
        inventario: Dict[str, Dict[str, Any]],
        carrito: Dict[str, Dict[str, Any]],
        total: float,
        ruta_ventas: Path | str = RUTA_VENTAS
) -> bool:
    """
    Descuenta el stock del inventario y registra la venta en data/ventas.txt (CF-10).
    Formato: fecha|total|codigo:cantidad;codigo:cantidad
    """
    if not carrito:
        print("[ERROR] El carrito esta vacio.")
        return False

    # 1. Descontar el stock en memoria
    for cod, item in carrito.items():
        inventario[cod]["stock"] -= item["cantidad"]

    # 2. Construir la linea de persistencia
    # Ejemplo: LAC001:2;BEB003:1
    detalle_codigos = ";".join(f"{item['codigo']}:{item['cantidad']}" for item in carrito.values())
    fecha_hoy = date.today().isoformat()
    linea_venta = f"{fecha_hoy}|{total:.1f}|{detalle_codigos}\n"

    # 3. Guardar al final de ventas.txt (modo 'a' con with, CR-05)
    ruta = Path(ruta_ventas)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(ruta, mode="a", encoding="utf-8") as f:
            f.write(linea_venta)
        print("[EXITO] Venta registrada exitosamente en historial y stock actualizado.")
        return True
    except OSError as e:
        print(f"[ERROR] No se pudo guardar la venta en '{ruta}': {e}")
        return False


if __name__ == "__main__":
    from persistencia import cargar_inventario

    print("--- PROBANDO MODULO DE VENTAS (src/ventas.py) ---")
    inv = cargar_inventario()
    cart = crear_carrito()

    # 1. Prueba de control de stock (CF-09)
    print("\n1. Intentar vender mas del stock disponible:")
    # BEB003 tiene stock de 8 unidades en nuestro data/inventario.txt
    agregar_al_carrito(inv, cart, "BEB003", 50)

    # 2. Agregar productos validos al carrito (CF-06)
    print("\n2. Construir una venta valida (superando $50.000 para probar descuento):")
    agregar_al_carrito(inv, cart, "LAC001", 10)  # 10 * 4200 = 42.000
    agregar_al_carrito(inv, cart, "ASE002", 2)   # 2 * 7500 = 15.000 -> Subtotal = 57.000

    # 3. Calcular totales y verificar descuento del 5% (CF-07)
    totales = calcular_totales(cart)
    print(formatear_detalle_venta(cart, totales))

    # 4. Prueba de pago insuficiente y cambio correcto (CF-08)
    print("4. Validacion de pago:")
    valido, _ = procesar_pago(totales["total"], 50000.0)
    print(f"Pago de $50.000 valido? {valido}")

    valido, cambio = procesar_pago(totales["total"], 60000.0)
    print(f"Pago de $60.000 valido? {valido} | Cambio: ${cambio:,.1f} COP")

    # 5. Confirmar venta y registrar en data/ventas.txt (CF-10)
    print("\n5. Confirmar venta y descontar stock:")
    stock_antes_lac = inv["LAC001"]["stock"]
    confirmar_venta(inv, cart, totales["total"])
    print(f"Stock de LAC001 antes: {stock_antes_lac} -> despues: {inv['LAC001']['stock']}")