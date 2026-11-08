import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tabulate import tabulate
from persistencia import cargar_inventario, guardar_inventario
import inventario as inv_modulo
import ventas as ven_modulo
import reportes as rep_modulo
import validaciones as val
from validaciones import ReglaNegocioError

def mostrar_menu_principal() -> None:
    print("\n" + "=" * 50)
    print("      TIENDAPY - TIENDA 'DON AURELIO'       ")
    print("=" * 50)
    print("  1. Registrar nuevo producto")
    print("  2. Consultar / Buscar productos")
    print("  3. Modificar precio o stock")
    print("  4. Eliminar producto")
    print("  5. Registrar nueva venta (Carrito)")
    print("  6. Alertas de stock bajo por proveedor")
    print("  7. Reporte de cierre de caja del dia")
    print("  8. Listar todo el inventario")
    print("  9. Guardar y Salir")
    print("=" * 50)

def flujo_registrar_producto(inventario: dict) -> None:
    print("\n--- REGISTRAR NUEVO PRODUCTO ---")
    while True:
        codigo = val.leer_texto("Ingrese codigo unico (ej. LAC001 o 'CANCELAR'): ").upper()
        if codigo == "CANCELAR":
            print("  [CANCELADO] Operacion abortada.")
            return
        if codigo in inventario:
            print(f"  [RECHAZADO] Ya existe un producto con el codigo '{codigo}'. Ingrese otro codigo o escriba CANCELAR.")
            continue
        break

    nombre = val.leer_texto("Nombre del producto: ")
    categoria = val.leer_categoria("Categoria (ingrese numero 1-5 o nombre): ")
    precio = val.leer_decimal("Precio de venta en COP: ", minimo=0.0, permitir_cero=False)
    stock = val.leer_entero("Stock inicial disponible: ", minimo=1)
    stock_min = val.leer_entero("Stock minimo para alerta: ", minimo=0)
    proveedor = val.leer_texto("Nombre del proveedor habitual: ")

    try:
        inv_modulo.agregar_producto(inventario, codigo, nombre, categoria, precio, stock, stock_min, proveedor)
        guardar_inventario(inventario)
        print(f"  [EXITO] Producto '{nombre}' ({codigo}) registrado correctamente.")
    except ReglaNegocioError as e:
        print(f"  [ERROR] {e}")

def flujo_consultar_producto(inventario: dict) -> None:
    print("\n--- CONSULTAR PRODUCTOS ---")
    print("  1. Buscar por codigo")
    print("  2. Filtrar por categoria")
    print("  3. Volver al menu principal")
    opcion = val.leer_entero("Seleccione opcion (1-3): ", minimo=1, maximo=3)

    if opcion == 1:
        codigo = val.leer_texto("Ingrese codigo a buscar (o 'CANCELAR'): ")
        if codigo.upper() == "CANCELAR":
            return
        prod = inv_modulo.consultar_por_codigo(inventario, codigo)
        if prod:
            tabla = [[k, v] for k, v in prod.items()]
            print("\n" + tabulate(tabla, headers=["Atributo", "Valor"], tablefmt="rounded_grid"))
        else:
            print(f"  [INFO] No se encontro ningun producto con el codigo '{codigo.upper()}'.")
    elif opcion == 2:
        cat = val.leer_categoria("Ingrese categoria a filtrar (1-5 o nombre): ")
        coincidencias = inv_modulo.buscar_por_categoria(inventario, cat)
        if coincidencias:
            filas = [[p["codigo"], p["nombre"], f"${p['precio']:,.1f}", p["stock"], p["proveedor"]] for p in coincidencias]
            print("\n" + tabulate(filas, headers=["Codigo", "Producto", "Precio", "Stock", "Proveedor"], tablefmt="rounded_grid"))
        else:
            print(f"  [INFO] No hay productos registrados en la categoria '{cat}'.")
    elif opcion == 3:
        return

def flujo_modificar_producto(inventario: dict) -> None:
    print("\n--- MODIFICAR PRODUCTO ---")
    codigo = val.leer_texto("Ingrese codigo del producto a modificar (o 'CANCELAR'): ").upper()
    if codigo == "CANCELAR":
        print("  [CANCELADO] Operacion abortada.")
        return

    prod = inv_modulo.consultar_por_codigo(inventario, codigo)
    if not prod:
        print(f"  [INFO] No se encontro ningun producto con el codigo '{codigo}'.")
        return

    print(f"Producto actual: {prod['nombre']} | Precio: ${prod['precio']} | Stock: {prod['stock']}")
    cambiar_precio = val.leer_texto("Desea cambiar el precio? (s/n): ").lower() in ["s", "si"]
    nuevo_precio = None
    if cambiar_precio:
        nuevo_precio = val.leer_decimal("Nuevo precio en COP: ", minimo=0.0, permitir_cero=False)

    cambiar_stock = val.leer_texto("Desea actualizar el stock? (s/n): ").lower() in ["s", "si"]
    nuevo_stock = None
    if cambiar_stock:
        nuevo_stock = val.leer_entero("Nuevo stock: ", minimo=1)

    if nuevo_precio is None and nuevo_stock is None:
        print("  [INFO] No se realizaron cambios en el producto.")
        return

    try:
        if inv_modulo.modificar_producto(inventario, codigo, nuevo_precio, nuevo_stock):
            guardar_inventario(inventario)
            print(f"  [EXITO] Producto '{codigo}' modificado con exito.")
    except ReglaNegocioError as e:
        print(f"  [ERROR] {e}")

def flujo_eliminar_producto(inventario: dict) -> None:
    print("\n--- ELIMINAR PRODUCTO ---")
    codigo = val.leer_texto("Ingrese codigo del producto a eliminar (o 'CANCELAR'): ").upper()
    if codigo == "CANCELAR":
        print("  [CANCELADO] Operacion abortada.")
        return

    prod = inv_modulo.consultar_por_codigo(inventario, codigo)
    if not prod:
        print(f"  [INFO] No se encontro ningun producto con el codigo '{codigo}'.")
        return

    confirmar = val.leer_texto(f"Confirma eliminar '{prod['nombre']}'? (s/n): ").lower()
    if confirmar in ["s", "si"]:
        try:
            eliminado = inv_modulo.eliminar_producto(inventario, codigo)
            guardar_inventario(inventario)
            print(f"  [EXITO] Producto '{eliminado['nombre']}' ({codigo}) eliminado del inventario.")
        except ReglaNegocioError as e:
            print(f"  [ERROR] {e}")
    else:
        print("  [CANCELADO] Operacion abortada.")

def flujo_venta_carrito(inventario: dict) -> None:
    print("\n--- REGISTRAR VENTA (CARRITO) ---")
    carrito = ven_modulo.crear_carrito()

    while True:
        codigo = val.leer_texto("Ingrese codigo de producto (o 'FIN' para pagar / 'CANCELAR'): ").upper()
        if codigo == "CANCELAR":
            print("  [CANCELADO] Venta cancelada.")
            return
        if codigo == "FIN":
            if not carrito:
                print("  [!] El carrito esta vacio. Agregue al menos un producto o escriba CANCELAR.")
                continue
            break

        prod = inv_modulo.consultar_por_codigo(inventario, codigo)
        if not prod:
            print(f"  [!] El producto '{codigo}' no existe en el inventario.")
            continue

        print(f"  Seleccionado: {prod['nombre']} (Stock disponible: {prod['stock']}, Precio: ${prod['precio']:,.1f})")
        cant = val.leer_entero("  Cantidad a vender (o 0 para descartar): ", minimo=0)
        if cant == 0:
            print("  [CANCELADO] Producto no agregado al carrito.")
            continue

        try:
            ven_modulo.agregar_al_carrito(inventario, carrito, codigo, cant)
            print(f"  [OK] '{prod['nombre']}' x{cant} agregado al carrito.")
        except ReglaNegocioError as e:
            print(f"  [RECHAZADO] {e}")

    totales = ven_modulo.calcular_totales(carrito)
    print(ven_modulo.formatear_detalle_venta(carrito, totales))

    while True:
        entrada = input(f"Monto recibido del cliente (Total ${totales['total']:,.1f}) [o 'CANCELAR']: ").strip()
        if entrada.upper() == "CANCELAR" or entrada == "0":
            print("  [CANCELADO] Venta cancelada. No se modifico el inventario.")
            return
        try:
            limpio = entrada.replace("$", "").replace(" ", "").replace(",", ".")
            monto = round(float(limpio), 2)
            if monto <= 0:
                print("  [!] El monto debe ser un numero mayor a cero.")
                continue
            cambio = ven_modulo.procesar_pago(totales["total"], monto)
            print(f"\n  [PAGO EXITOSO] Cambio a entregar: ${cambio:,.1f} COP")
            break
        except ValueError:
            print("  [!] Entrada invalida. Ingrese un valor numerico valido o 'CANCELAR'.")
        except ReglaNegocioError as e:
            print(f"  [ERROR] {e}")
            print("  Reintentando pago...")

    try:
        ven_modulo.confirmar_venta(inventario, carrito, totales["total"])
        print("  [EXITO] Venta registrada exitosamente y stock actualizado.")
    except ReglaNegocioError as e:
        print(f"  [ERROR] {e}")

def listar_todo_el_inventario(inventario: dict) -> None:
    if not inventario:
        print("\n[INFO] El inventario esta vacio.")
        return
    filas = [
        [p["codigo"], p["nombre"], p["categoria"], f"${p['precio']:,.1f}", p["stock"], p["stock_minimo"], p["proveedor"]]
        for p in inventario.values()
    ]
    print("\n" + tabulate(filas, headers=["Codigo", "Producto", "Categoria", "Precio", "Stock", "Min.", "Proveedor"], tablefmt="rounded_grid"))

def main() -> None:
    inventario = cargar_inventario()
    print("[INICIO] Base de datos e inventario cargados exitosamente.")

    while True:
        try:
            mostrar_menu_principal()
            opcion = val.leer_entero("Seleccione una opcion (1-9): ", minimo=1, maximo=9)

            if opcion == 1:
                flujo_registrar_producto(inventario)
            elif opcion == 2:
                flujo_consultar_producto(inventario)
            elif opcion == 3:
                flujo_modificar_producto(inventario)
            elif opcion == 4:
                flujo_eliminar_producto(inventario)
            elif opcion == 5:
                flujo_venta_carrito(inventario)
            elif opcion == 6:
                print(rep_modulo.generar_alerta_stock(inventario))
            elif opcion == 7:
                fecha_input = input("Ingrese fecha para el cierre (YYYY-MM-DD) o Enter para hoy (o 'CANCELAR'): ").strip()
                if fecha_input.upper() == "CANCELAR":
                    print("  [CANCELADO] Consulta de cierre cancelada.")
                    continue
                fecha_cierre = fecha_input if fecha_input else None
                print(rep_modulo.generar_cierre_del_dia(inventario, fecha_cierre=fecha_cierre))
            elif opcion == 8:
                listar_todo_el_inventario(inventario)
            elif opcion == 9:
                guardar_inventario(inventario)
                print("\n[FIN] Inventario guardado. Hasta pronto Don Aurelio!\n")
                break
            else:
                print("  [!] Opcion no valida. Seleccione entre 1 y 9.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n[AVISO] Salida forzada. Guardando datos de forma segura...")
            guardar_inventario(inventario)
            break
        except Exception as e:
            print(f"\n[ERROR INESPERADO] {e}. Continuando ejecucion...")

if __name__ == "__main__":
    main()