from datetime import date
from pathlib import Path
from typing import Dict, Any, Optional
from collections import defaultdict
from tabulate import tabulate
from persistencia import RUTA_VENTAS, cargar_ventas

def generar_alerta_stock(inventario: Dict[str, Dict[str, Any]]) -> str:
    productos_alerta = [
        prod for prod in inventario.values()
        if prod["stock"] <= prod["stock_minimo"]
    ]

    if not productos_alerta:
        return "\n[OK] El inventario esta optimo. No hay productos en o por debajo del stock minimo."

    por_proveedor = defaultdict(list)
    for prod in productos_alerta:
        por_proveedor[prod["proveedor"]].append(prod)

    lineas_reporte = [
        "\n=======================================================",
        "        ALERTAS DE REABASTECIMIENTO DE STOCK           ",
        "======================================================="
    ]

    for proveedor, lista in sorted(por_proveedor.items()):
        filas = []
        for p in lista:
            estado = "AGOTADO" if p["stock"] == 0 else "BAJO STOCK"
            pedir = max(p["stock_minimo"] * 2 - p["stock"], p["stock_minimo"])
            filas.append([
                p["codigo"],
                p["nombre"],
                p["categoria"],
                p["stock"],
                p["stock_minimo"],
                estado,
                f"+{pedir} uds"
            ])

        encabezados = ["Codigo", "Producto", "Categoria", "Stock", "Min.", "Estado", "Sugerido"]
        tabla = tabulate(filas, headers=encabezados, tablefmt="rounded_grid")
        lineas_reporte.append(f"\nProveedor: [ {proveedor} ]")
        lineas_reporte.append(tabla)

    return "\n".join(lineas_reporte)

def generar_cierre_del_dia(
    inventario: Dict[str, Dict[str, Any]],
    ruta_ventas: Path | str = RUTA_VENTAS,
    fecha_cierre: Optional[str] = None
) -> str:
    if not fecha_cierre:
        fecha_cierre = date.today().isoformat()

    todas_ventas = cargar_ventas(ruta_ventas)
    ventas_dia = [v for v in todas_ventas if v["fecha"] == fecha_cierre]

    if not ventas_dia:
        return f"\n[INFO] No hay ventas registradas para el dia {fecha_cierre}."

    total_vendido = sum(v["total"] for v in ventas_dia)
    num_transacciones = len(ventas_dia)
    ticket_promedio = total_vendido / num_transacciones if num_transacciones > 0 else 0.0

    unidades_por_cod = defaultdict(int)
    categorias_activas = set()

    for v in ventas_dia:
        for item in v["items"]:
            c = item["codigo"]
            cant = item["cantidad"]
            unidades_por_cod[c] += cant
            if c in inventario:
                categorias_activas.add(inventario[c]["categoria"])

    if unidades_por_cod:
        cod_top = max(unidades_por_cod, key=unidades_por_cod.get)
        nombre_top = inventario.get(cod_top, {}).get("nombre", cod_top)
        top_str = f"{nombre_top} ({cod_top}) con {unidades_por_cod[cod_top]} unidades"
    else:
        top_str = "N/A"

    vendidos = set(unidades_por_cod.keys())
    sin_ventas = [
        f"{p['nombre']} ({p['codigo']})"
        for cod, p in inventario.items()
        if cod not in vendidos
    ]

    resumen = [
        ["Fecha de Cierre:", fecha_cierre],
        ["Total Vendido:", f"${total_vendido:,.1f} COP"],
        ["Numero de Ventas:", num_transacciones],
        ["Ticket Promedio:", f"${ticket_promedio:,.1f} COP"],
        ["Producto Mas Vendido:", top_str],
        ["Categorias con Movimiento:", ", ".join(sorted(categorias_activas)) or "Ninguna"]
    ]

    tabla_kpi = tabulate(resumen, tablefmt="fancy_grid")

    salida = [
        "\n=======================================================",
        f"          CIERRE DE CAJA DEL DIA ({fecha_cierre})     ",
        "=======================================================",
        tabla_kpi
    ]

    if sin_ventas:
        salida.append(f"\nProductos sin rotacion en la fecha ({len(sin_ventas)} referencias):")
        salida.append("  * " + "\n  * ".join(sin_ventas[:10]))
        if len(sin_ventas) > 10:
            salida.append(f"  ... y {len(sin_ventas) - 10} referencias mas.")

    return "\n".join(salida)