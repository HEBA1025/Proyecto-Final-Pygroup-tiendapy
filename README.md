# TiendaPy - Sistema de Gestión para Tienda "Don Aurelio"

Proyecto final para el curso **Python 0 a 100** dictado por el capítulo estudiantil **ACM UD** de la Universidad Distrital Francisco José de Caldas.

---

### Datos del Estudiante
* **Nombre completo:** Edward Alejandro Hernandez Barrero
* **Código estudiantil:** 20261020055
* **Correo institucional:** eahernandezb@udistrital.edu.co
* **Modalidad:** Individual
* **Repositorio GitHub:** [https://github.com/HEBA1025/Proyecto-Final-Pygroup-tiendapy](https://github.com/HEBA1025/Proyecto-Final-Pygroup-tiendapy)

---

## 1. Contexto de la Problemática

Don Aurelio administra desde hace quince años una tienda de barrio en la localidad de Kennedy (Bogotá). Al manejar cerca de 150 referencias y atender un promedio de 80 clientes diarios registrando las operaciones en un cuaderno de papel o de memoria, enfrentaba constantes contratiempos que perjudicaban la rentabilidad del negocio:

| Problema en la tienda "Don Aurelio" | Solución implementada en TiendaPy | Módulo |
|---|---|:---:|
| Desabastecimiento inesperado al agotar productos | Alertas automáticas de stock bajo y agotados agrupados por proveedor | M3 |
| Errores de cálculo en sumas manuales y devueltas | Carrito de compras automático con cálculo de subtotales, descuentos y cambio | M2 |
| Referencias acumuladas sin rotación ni ventas | Reporte de cierre diario con listado de productos sin ventas en la fecha | M4 |
| Pérdida, deterioro o daño del cuaderno de cuentas | Persistencia estructurada en archivos de texto plano (`data/`) | M5 |
| Pedidos ineficientes a proveedores | Reporte de reabastecimiento con cálculo de unidades sugeridas a pedir | M3 |
| Ausencia de balance o cierre de caja diario | Estadísticas consolidadas: total vendido, transacciones, ticket promedio y producto líder | M4 |

---

## 2. Funcionalidades del Sistema

* **M1. Gestión de inventario:** Registro de nuevos productos con validación de código único, consulta detallada por código, búsqueda y filtrado por categoría oficial (Lácteos, Bebidas, Aseo, Abarrotes, Snacks), modificación de precio y existencias, y eliminación de productos.
* **M2. Registro de ventas (Carrito):** Creación de ventas compuestas por múltiples productos, cálculo de subtotal, aplicación automática de descuentos por volumen, cálculo del cambio a entregar, soporte para descarte de ítems o cancelación de la venta, y descuento de existencias al confirmar.
* **M3. Alertas de stock:** Detección de productos con existencias menores o iguales al stock mínimo configurado, agrupados por su proveedor habitual, diferenciando entre productos en bajo stock y productos agotados (stock 0), con estimación de unidades sugeridas para reabastecimiento.
* **M4. Cierre del día:** Generación del reporte de caja diario (de la fecha actual o consultando una fecha histórica): total en dinero recaudado, número de ventas, ticket promedio por cliente, producto más vendido, categorías con movimiento comercial y lista de productos sin rotación.
* **M5. Persistencia:** Carga inicial automática de datos desde archivos de texto plano, guardado sincronizado tras modificaciones y ventas, y almacenamiento seguro al salir o ante una interrupción.
* **M6. Menú interactivo:** Interfaz de consola diseñada para usuarios sin formación técnica, con validación continua de entradas numéricas y de texto para evitar que el programa se detenga por errores de digitación.

---

## 3. Requisitos del Sistema

* **Python 3.10 o superior.**
* **Librería externa:** [`tabulate`](https://pypi.org/project/tabulate/) (versión 0.9.0 o superior), empleada para la presentación limpia de tablas y reportes en consola.

---

## 4. Instalación y Ejecución

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/HEBA1025/Proyecto-Final-Pygroup-tiendapy.git
cd Proyecto-Final-Pygroup-tiendapy
```

### Paso 2: Crear y activar el entorno virtual (`venv`)

* **En Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

* **En Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

* **En Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Paso 3: Instalar las dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Ejecutar la aplicación
Ejecutar siempre desde la raíz del proyecto para asegurar la correcta lectura de la carpeta de datos:
```bash
python src/main.py
```

---

## 5. Estructura del Repositorio

La organización del proyecto sigue una estructura modular orientada a separar la lógica de negocio, la persistencia y la interfaz de usuario:

```text
tiendapy/
├── README.md               # Documentación técnica completa del proyecto
├── requirements.txt        # Definición de dependencias externas (tabulate)
├── data/
│   ├── inventario.txt      # Archivo de texto plano con los productos del inventario
│   └── ventas.txt          # Historial persistente de todas las ventas realizadas
└── src/
    ├── __init__.py         # Inicializador de paquete
    ├── main.py             # Menú principal y control del flujo de usuario
    ├── inventario.py       # Operaciones CRUD y consultas del catálogo
    ├── ventas.py           # Gestión del carrito, cálculo de totales, descuentos y pagos
    ├── reportes.py         # Generación de alertas de inventario y cierre de caja
    ├── persistencia.py     # Lectura, escritura y sanitización de archivos de datos
    └── validaciones.py     # Captura segura de datos en consola y excepciones de negocio
```

---

## 6. Formato de Persistencia de Datos

Los datos se guardan en la carpeta `data/` usando archivos de texto plano con delimitador de barra vertical (`|`):

### Inventario (`data/inventario.txt`)
Cada línea representa un producto con el siguiente esquema de 7 campos:
`codigo|nombre|categoria|precio|stock|stock_minimo|proveedor`

Ejemplo:
```text
LAC001|Leche entera 1L|Lacteos|4200.0|35|10|Alqueria
BEB003|Gaseosa 1.5L|Bebidas|5800.0|8|12|Postobon
ASE002|Detergente 500g|Aseo|7500.0|20|5|Distribuidora Norte
ABA001|Arroz 1kg|Abarrotes|4500.0|50|15|Diana
SNK001|Papas Fritas 115g|Snacks|3200.0|5|10|FritoLay
```

### Historial de Ventas (`data/ventas.txt`)
Cada línea registra una transacción confirmada con el siguiente esquema de 3 campos:
`fecha|total|codigo:cantidad;codigo:cantidad`

Ejemplo:
```text
2026-11-05|54150.0|LAC001:10;ASE002:2
2026-11-06|14200.0|LAC001:2;BEB003:1
```

* **Tratamiento de archivos corruptos o inexistentes:**
  * Si `inventario.txt` no existe, el programa lo notifica e inicializa automáticamente un archivo vacío en disco.
  * Si una línea dentro de los archivos presenta un número incorrecto de campos o valores numéricos corruptos, se omite mostrando una advertencia informativa y se continúa con el resto de registros válidos sin interrumpir el funcionamiento.

---

## 7. Reglas de Negocio Implementadas

1. **Control de disponibilidad:** No es posible agregar al carrito ni vender una cantidad superior a las existencias reales en inventario.
2. **Precios y cantidades válidas:** No se aceptan valores numéricos negativos ni iguales a cero al ingresar precios, existencias iniciales o cantidades de venta.
3. **Escala de descuentos por volumen de compra:**
   * Subtotales iguales o superiores a **$50.000 COP**: reciben un **5 %** de descuento sobre el subtotal.
   * Subtotales iguales o superiores a **$100.000 COP**: reciben un **10 %** de descuento sobre el subtotal.
4. **Validación de pagos y cambio:** El monto entregado por el cliente debe cubrir la totalidad del importe. Si el dinero es insuficiente, el sistema señala el valor faltante y permite reintentar o cancelar la venta. Si el pago es suficiente, calcula el cambio exacto.
5. **Unicidad de códigos:** Los códigos de producto se normalizan a mayúsculas y no pueden repetirse.
6. **Clasificación de alertas:** Todo producto con existencia igual a cero se etiqueta explícitamente en el reporte de alertas como `AGOTADO`.

---

## 8. Decisiones de Diseño y Arquitectura

* **Programación modular con estructuras nativas (sin clases):** Acorde con los objetivos de un curso de fundamentos de programación de segundo semestre, se prescindió del uso de clases u objetos complejos. Los productos se modelan como diccionarios y el inventario como un diccionario indexado por código (`{codigo: datos_producto}`), lo cual asegura consultas y modificaciones inmediatas en tiempo constante $O(1)$.
* **Separación de responsabilidades:** La interfaz de consola (`main.py`) no interactúa directamente con los archivos; delega las operaciones a los módulos correspondientes (`inventario.py`, `ventas.py`, `reportes.py` y `persistencia.py`).
* **Señalización de reglas de negocio con excepciones:** Las violaciones a las reglas comerciales disparan una excepción personalizada `ReglaNegocioError` (heredada de `Exception`), la cual es capturada de forma controlada en la capa de interacción para informar al usuario sin abortar la aplicación.
* **Manejo seguro de archivos y rutas:** Todas las aperturas de archivos se realizan mediante context managers (`with open(...)`), garantizando el cierre correcto de recursos ante cualquier error. Las rutas se gestionan con la librería estándar `pathlib.Path` referenciadas a la raíz del proyecto, evitando fallos si el comando se invoca desde subdirectorios.
