from typing import Optional

class ReglaNegocioError(Exception):
    pass

CATEGORIAS_OFICIALES = ["Lacteos", "Bebidas", "Aseo", "Abarrotes", "Snacks"]

def normalizar_texto(texto: str) -> str:
    reemplazos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u"}
    t = texto.strip().lower()
    for con_tilde, sin_tilde in reemplazos.items():
        t = t.replace(con_tilde, sin_tilde)
    return t

def leer_entero(mensaje: str, minimo: Optional[int] = None, maximo: Optional[int] = None) -> int:
    while True:
        entrada = input(mensaje).strip()
        try:
            valor = int(entrada)
            if minimo is not None and valor < minimo:
                print(f"  [!] El valor debe ser mayor o igual a {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  [!] El valor debe ser menor o igual a {maximo}.")
                continue
            return valor
        except ValueError:
            print("  [!] Entrada invalida. Ingrese un numero entero valido.")

def leer_decimal(mensaje: str, minimo: Optional[float] = 0.0, permitir_cero: bool = False) -> float:
    while True:
        entrada = input(mensaje).strip().replace("$", "").replace(" ", "").replace(",", ".")
        try:
            valor = float(entrada)
            if minimo is not None:
                if permitir_cero and valor < minimo:
                    print(f"  [!] El valor debe ser mayor o igual a {minimo}.")
                    continue
                if not permitir_cero and valor <= minimo:
                    print(f"  [!] El valor debe ser mayor a {minimo}.")
                    continue
            return round(valor, 2)
        except ValueError:
            print("  [!] Entrada invalida. Ingrese un valor numerico valido.")

def leer_texto(mensaje: str) -> str:
    while True:
        texto = input(mensaje).strip()
        if texto:
            return texto
        print("  [!] Este campo no puede dejarse vacio.")

def leer_categoria(mensaje: str) -> str:
    opciones_texto = ", ".join(f"{i+1}. {cat}" for i, cat in enumerate(CATEGORIAS_OFICIALES))
    print(f"  Categorias validas: {opciones_texto}")
    while True:
        entrada = leer_texto(mensaje).strip()
        if entrada.isdigit():
            idx = int(entrada) - 1
            if 0 <= idx < len(CATEGORIAS_OFICIALES):
                return CATEGORIAS_OFICIALES[idx]
        cat_entrada = normalizar_texto(entrada)
        for oficial in CATEGORIAS_OFICIALES:
            oficial_norm = normalizar_texto(oficial)
            if oficial_norm == cat_entrada or cat_entrada in oficial_norm or oficial_norm.rstrip("s") == cat_entrada.rstrip("s"):
                return oficial
        print(f"  [!] Categoria invalida. Opciones: {opciones_texto}")