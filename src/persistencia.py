"""
Modulo de persistencia para TiendaPy.
Encargado de la lectura y escritura segura de archivos de texto plano.
Cumple con CF-01, CR-03, CR-04 y CR-05.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Ruta base del proyecto (la carpeta tiendapy/ independientemente de donde se ejecute)
BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_INVENTARIO = BASE_DIR / "data" / "inventario.txt"
RUTA_VENTAS = BASE_DIR / "data" / "ventas.txt"


def cargar_inventario(ruta_archivo: Path | str = RUTA_INVENTARIO) -> Dict[str, Dict[str, Any]]:
    """
    Carga los productos desde el archivo de texto plano.

    Formato esperado por linea:
    codigo|nombre|categoria|precio|stock|stock_minimo|proveedor

    Retorna:
        Dict[str, dict]: Diccionario de productos indexado por su codigo unico.
    """
    inventario: Dict[str, Dict[str, Any]] = {}
    ruta = Path(ruta_archivo)

    # CR-03: Si el archivo no existe, crearlo vacio e iniciar sin fallar
    if not ruta.exists():
        print(f"[INFO] El archivo '{ruta}' no existe. Creando archivo vacio...")
        ruta.parent.mkdir(parents=True, exist_ok=True)
        try:
            # CR-05: Uso de context manager with
            with open(ruta, mode="w", encoding="utf-8") as f:
                pass
        except OSError as e:
            print(f"[ERROR] No se pudo crear el archivo '{ruta}': {e}")
        return inventario

    # CR-05: Lectura segura con with
    try:
        with open(ruta, mode="r", encoding="utf-8") as archivo:
            for num_linea, linea in enumerate(archivo, start=1):
                linea_limpia = linea.strip()

                # Ignorar lineas vacias
                if not linea_limpia:
                    continue

                partes = linea_limpia.split("|")

                # CR-04: Validar numero exacto de columnas (7 atributos segun Tabla 1)
                if len(partes) != 7:
                    print(f"[ADVERTENCIA] Linea {num_linea} corrupta (esperaba 7 campos, recibio {len(partes)}): '{linea_limpia}'. Se omite.")
                    continue

                codigo, nombre, categoria, precio_str, stock_str, stock_min_str, proveedor = [p.strip() for p in partes]

                # CR-04: Validacion de tipos numericos y valores positivos (CR-02)
                try:
                    precio = float(precio_str)
                    stock = int(stock_str)
                    stock_minimo = int(stock_min_str)
                except ValueError:
                    print(f"[ADVERTENCIA] Linea {num_linea} corrupta (tipos numericos invalidos): '{linea_limpia}'. Se omite.")
                    continue

                if precio <= 0 or stock < 0 or stock_minimo < 0:
                    print(f"[ADVERTENCIA] Linea {num_linea} corrupta (valores fuera de rango): '{linea_limpia}'. Se omite.")
                    continue

                # CR-04: Validar que el codigo no se repita dentro del archivo
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
    """
    Guarda el diccionario de inventario en el archivo de texto plano.
    Cumple con CR-05 y formato oficial delimitado por pipes.
    """
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


if __name__ == "__main__":
    print("--- Probando modulo de persistencia (src/persistencia.py) ---")

    # 1. Probar lectura del inventario actual
    datos = cargar_inventario()
    print(f"\n[OK] Productos cargados correctamente: {len(datos)}")
    for cod, info in datos.items():
        print(f"  - [{cod}] {info['nombre']} | Cat: {info['categoria']} | ${info['precio']} | Stock: {info['stock']} (Min: {info['stock_minimo']})")

    # 2. Prueba de robustez: archivo que no existe (CR-03)
    print("\n--- Prueba CR-03: Archivo inexistente ---")
    ruta_fantasma = BASE_DIR / "data" / "archivo_fantasma.txt"
    datos_inexistente = cargar_inventario(ruta_fantasma)
    print(f"[OK] Inventario retornado correctamente (vacio): {datos_inexistente}")
    if ruta_fantasma.exists():
        ruta_fantasma.unlink()