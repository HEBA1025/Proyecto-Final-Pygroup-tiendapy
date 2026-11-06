"""
Modulo de reportes y analisis para TiendaPy.
Genera alertas de reabastecimiento y el reporte de cierre del dia.
Cumple con CF-11, CF-12, M3, M4 y CR-05.
"""

from datetime import date
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict
from tabulate import tabulate
from persistencia import BASE_DIR, RUTA_VENTAS, RUTA_INVENTARIO


def cargar_ventas_desde_archivo(ruta_ventas: Path | str = RUTA_VENTAS) -> List[Dict[str, Any]]:
    """
    Lee de forma segura 'data/ventas.txt' y retorna la lista de ventas (CR-05).
    Formato esperado: fecha|total|codigo:cantidad;codigo:cantidad
    """
    ruta = Path(ruta_ventas)
    ventas = []

    if not ruta.exists():
        return ventas

    try:
        with open(ruta, mode="r", encoding="utf-8") as f:
            for num_linea, linea in enumerate(f, start=1):
                linea = linea.strip()
                if not linea:
                    continue

                partes = linea.split("|")
                if len(partes) != 3:
                    continue  # Omite lineas corruptas con seguridad (CR-04)

                fecha_str, total_str, items_str = partes
                try:
                    total = float(total_str)
                except ValueError:
                    continue

                # Parsear items: codigo:cantidad
                detalles = []
                for item_str in items_str.split(";"):
                    if ":" in item_str:
                        cod, cant = item_str.split(":", 1)
                        try:
                            detalles.append({"codigo": cod.strip(), "cantidad": int(cant)})
                        except ValueError:
                            continue

                ventas.append({
                    "fecha": fecha_str.strip(),
                    "total": total,
                    "items": detalles
                })
    except OSError as e:
        print(f"[ERROR] No se pudo leer el archivo de ventas '{ruta}': {e}")

    return ventas


def generar_alerta_stock(inventario: Dict[str, Dict[str, Any]]) -> str:
    """
    Genera el reporte de alertas de productos cuyo stock es <= stock_minimo,
    agrupados por proveedor e identificando los agotados (CF-11, M3, Regla 3.3).
    """
    # 1. Filtrar productos bajo o en stock minimo
    productos_alerta = [
        prod for prod in inventario.values()
        if prod["stock"] <= prod["stock_minimo"]
    ]

    if not productos_alerta:
        return "\n[OK] El inventario esta saludable. Ningun producto requiere reabastecimiento."

    # 2. Agrupar por proveedor
    por_proveedor = defaultdict(list)
    for prod in productos_alerta:
        por_proveedor[prod["proveedor"]].append(prod)

    reporte = ["\n==================================================",
               "           ALERTA DE REABASTECIMIENTO (CF-11)      ",
               "=================================================="]

    for proveedor, prods in sorted(por_proveedor.items()):
        filas = []
        for p in prods:
            estado = "AGOTADO" if p["stock"] == 0 else "BAJO STOCK"
            sugerido = max(p["stock_minimo"] * 2 - p["stock"], p["stock_minimo"])
            filas.append([
                p["codigo"],
                p["nombre"],
                p["categoria"],
                p["stock"],
                p["stock_minimo"],
                estado,
                f"+{sugerido} uds"
            ])

        encabezados = ["Codigo", "Producto", "Categoria", "Stock", "Min.", "Estado", "Pedir"]
        tabla = tabulate(filas, headers=encabezados, tablefmt="rounded_grid")
        reporte.append(f"\nProveedor: [ {proveedor} ]")
        reporte.append(tabla)

    return "\n".join(reporte)


def generar_cierre_del_dia(
        inventario: Dict[str, Dict[str, Any]],
        ruta_ventas: Path | str = RUTA_VENTAS,
        fecha_cierre: Optional[str] = None
) -> str:
    """
    Genera el reporte de cierre del dia (CF-12, M4):
    - Total vendido ($ COP)
    - Numero de transacciones
    - Ticket promedio
    - Producto mas vendido
    - Productos sin ventas
    - Categorias con movimiento
    """
    if fecha_cierre is None:
        fecha_cierre = date.today().isoformat()

    todas_ventas = cargar_ventas_desde_archivo(ruta_ventas)
    ventas_dia = [v for v in todas_ventas if v["fecha"] == fecha_cierre]

    if not ventas_dia:
        return f"\n[INFO] No se registraron ventas para la fecha {fecha_cierre}."

    total_vendido = sum(v["total"] for v in ventas_dia)
    num_transacciones = len(ventas_dia)
    ticket_promedio = total_vendido / num_transacciones if num_transacciones > 0 else 0.0

    # Estadisticas por producto vendido
    unidades_por_producto = defaultdict(int)
    recaudacion_por_producto = defaultdict(float)
    categorias_con_movimiento = set()

    for v in ventas_dia:
        for item in v["items"]:
            cod = item["codigo"]
            cant = item["cantidad"]
            unidades_por_producto[cod] += cant
            if cod in inventario:
                prod = inventario[cod]
                categorias_con_movimiento.add(prod["categoria"])
                recaudacion_por_producto[cod] += cant * prod["precio"]

    # Producto mas vendido
    if unidades_por_producto:
        cod_top = max(unidades_por_producto, key=unidades_por_producto.get)
        nombre_top = inventario.get(cod_top, {}).get("nombre", cod_top)
        top_unidades = unidades_por_producto[cod_top]
        top_producto_str = f"{nombre_top} ({cod_top}) con {top_unidades} unidades"
    else:
        top_producto_str = "N/A"

    # Productos sin ventas en el dia
    codigos_vendidos = set(unidades_por_producto.keys())
    prods_sin_ventas = [
        f"{p['nombre']} ({p['codigo']})"
        for cod, p in inventario.items()
        if cod not in codigos_vendidos
    ]

    # Construir reporte visual
    resumen_kpi = [
        ["Fecha del reporte:", fecha_cierre],
        ["Total Vendido:", f"${total_vendido:,.1f} COP"],
        ["Numero de Transacciones:", num_transacciones],
        ["Ticket Promedio:", f"${ticket_promedio:,.1f} COP"],
        ["Producto Mas Vendido:", top_producto_str],
        ["Categorias con Movimiento:", ", ".join(sorted(categorias_con_movimiento)) or "Ninguna"]
    ]

    tabla_kpi = tabulate(resumen_kpi, tablefmt="fancy_grid")

    salida = [
        "\n==================================================",
        f"          CIERRE DE CAJA DEL DIA ({fecha_cierre}) ",
        "==================================================",
        tabla_kpi
    ]

    if prods_sin_ventas:
        salida.append(f"\nProductos sin rotacion en la fecha ({len(prods_sin_ventas)} refs):")
        salida.append("  * " + "\n  * ".join(prods_sin_ventas[:10]))
        if len(prods_sin_ventas) > 10:
            salida.append(f"  ... y {len(prods_sin_ventas) - 10} referencias mas.")

    return "\n".join(salida)


if __name__ == "__main__":
    from persistencia import cargar_inventario

    print("--- PROBANDO MODULO DE REPORTES (src/reportes.py) ---")
    inv = cargar_inventario()

    # 1. Probar Alerta de Stock (CF-11)
    print(generar_alerta_stock(inv))

    # 2. Probar Cierre del Dia con la venta que acabamos de registrar (CF-12)
    print(generar_cierre_del_dia(inv))