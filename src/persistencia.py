from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_INVENTARIO = BASE_DIR / "data" / "inventario.txt"
RUTA_VENTAS = BASE_DIR / "data" / "ventas.txt"

def cargar_inventario(ruta_archivo: Path | str = RUTA_INVENTARIO) -> Dict[str, Dict[str, Any]]:
    inventario = {}
    ruta = Path(ruta_archivo)

    if not ruta.exists():
        print(f"[INFO] El archivo '{ruta}' no existe. Creando archivo vacio...")
        ruta.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(ruta, mode="w", encoding="utf-8") as f:
                pass
        except OSError as e:
            print(f"[ERROR] No se pudo crear el archivo '{ruta}': {e}")
        return inventario

    try:
        with open(ruta, mode="r", encoding="utf-8") as archivo:
            for num_linea, linea in enumerate(archivo, start=1):
                linea_limpia = linea.strip()
                if not linea_limpia:
                    continue

                partes = linea_limpia.split("|")
                if len(partes) != 7:
                    print(f"[ADVERTENCIA] Linea {num_linea} corrupta (esperaba 7 campos, recibio {len(partes)}). Se omite.")
                    continue

                codigo, nombre, categoria, precio_str, stock_str, stock_min_str, proveedor = [p.strip() for p in partes]

                try:
                    precio = float(precio_str)
                    stock = int(stock_str)
                    stock_minimo = int(stock_min_str)
                except ValueError:
                    print(f"[ADVERTENCIA] Linea {num_linea} corrupta (tipos numericos invalidos). Se omite.")
                    continue

                if precio <= 0 or stock < 0 or stock_minimo < 0:
                    print(f"[ADVERTENCIA] Linea {num_linea} corrupta (valores fuera de rango). Se omite.")
                    continue

                if codigo in inventario:
                    print(f"[ADVERTENCIA] Linea {num_linea} ignorada: codigo duplicado '{codigo}'.")
                    continue

                inventario[codigo] = {
                    "codigo": codigo,
                    "nombre": nombre,
                    "categoria": categoria,
                    "precio": precio,
                    "stock": stock,
                    "stock_minimo": stock_minimo,
                    "proveedor": proveedor
                }
    except OSError as e:
        print(f"[ERROR] Ocurrio un error al leer el archivo '{ruta}': {e}")

    return inventario

def guardar_inventario(inventario: Dict[str, Dict[str, Any]], ruta_archivo: Path | str = RUTA_INVENTARIO) -> bool:
    ruta = Path(ruta_archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(ruta, mode="w", encoding="utf-8") as archivo:
            for prod in inventario.values():
                linea = f"{prod['codigo']}|{prod['nombre']}|{prod['categoria']}|{prod['precio']}|{prod['stock']}|{prod['stock_minimo']}|{prod['proveedor']}\n"
                archivo.write(linea)
        return True
    except OSError as e:
        print(f"[ERROR] No se pudo guardar el inventario en '{ruta}': {e}")
        return False

def cargar_ventas(ruta_archivo: Path | str = RUTA_VENTAS) -> List[Dict[str, Any]]:
    ventas = []
    ruta = Path(ruta_archivo)

    if not ruta.exists():
        return ventas

    try:
        with open(ruta, mode="r", encoding="utf-8") as archivo:
            for num_linea, linea in enumerate(archivo, start=1):
                linea_limpia = linea.strip()
                if not linea_limpia:
                    continue

                partes = linea_limpia.split("|")
                if len(partes) != 3:
                    print(f"[ADVERTENCIA] Linea {num_linea} corrupta en ventas. Se omite.")
                    continue

                fecha_str, total_str, items_str = partes
                try:
                    total = float(total_str)
                except ValueError:
                    print(f"[ADVERTENCIA] Linea {num_linea} corrupta en ventas (total invalido). Se omite.")
                    continue

                detalles = []
                for item_str in items_str.split(";"):
                    item_str = item_str.strip()
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
        print(f"[ERROR] Error de lectura en '{ruta}': {e}")

    return ventas

def registrar_venta_archivo(linea_venta: str, ruta_archivo: Path | str = RUTA_VENTAS) -> bool:
    ruta = Path(ruta_archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(ruta, mode="a", encoding="utf-8") as archivo:
            archivo.write(linea_venta)
        return True
    except OSError as e:
        print(f"[ERROR] No se pudo registrar la venta en '{ruta}': {e}")
        return False