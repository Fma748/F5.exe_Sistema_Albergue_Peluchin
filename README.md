# GRUPO 3
# SISTEMA DE INVENTARIO Y SUMINISTROS  

# DESCRIPCIÓN DEL PROYECTO 

Lo que nuestro equipo busca crear es un sistema de inventario y suministros que apoye a tener una mejor organización con los suministros y el inventario de un albergue. Para implementar esta idea, tras un breve estudio e investigación, tomamos en cuenta el "Albergue Peluchin".

El Albergue Peluchin no cuenta con un sistema de inventario, por lo que el registro de alimentos e insumos, las donaciones recibidas y su entrega a las mascotas se llevan sin un control organizado. Esto provoca desorden, pérdida de recursos y dificultades para dar seguimiento a las actividades de asistencia.

# OBJETIVO GENERAL

Nuestro objetivo como equipo es desarrollar un sistema de inventario y suministros para el Albergue Peluchin que permita controlar los alimentos e insumos, gestionar las donaciones, dar seguimiento a los cuidados especiales de las mascotas y facilitar el intercambio de información con otras instituciones, evitando la pérdida de recursos y mejorando su uso.

# INTEGRANTES

| N° | Nombre completo | Rol | GitHub |
|---|---|---|---|
| 1 | Medinaceli Andrade Fernando Yeray | Scrum Master | @Fma748 |
| 2 | Mamani Quispe Elvis | Lider de Documento| @BiscochoTK |
| 3 | Apaza Nistaza David Abraham | Developer | @DavidNistaza07-pixel |
| 4 | Magueño Cano Benjamin | Developer | @maguenobenjamin-maker |
| 5 | Nina Garcia Hugo Marcelo | Product Owner| @Cannzert |

# DESCRIPCIÓN

El proyecto **F5.exe – Sistema de Inventario y Suministros Albergue Peluchin** consiste en el desarrollo de un programa informático orientado a mejorar el registro, la organización y el control de los alimentos, insumos y donaciones del albergue.

El sistema facilita el manejo de la información mediante funcionalidades que permiten registrar productos, controlar sus cantidades disponibles, gestionar sus entradas y salidas, identificar productos próximos a vencer y realizar un seguimiento de las donaciones recibidas.

Asimismo, contempla el registro de las mascotas, de lo que consume cada una y de los cuidados especiales que reciben, permitiendo mantener una mejor organización de la información y una distribución más ordenada de los suministros.


# 1. REQUISITOS

Para instalar y ejecutar el proyecto se necesitan las siguientes herramientas y tecnologías.

## 1.1. Herramientas y versiones

| Herramienta | Versión de referencia | Función |
|---|---|---|
| Visual Studio Code | Versión estable | Editor de código fuente |
| XAMPP | 8.5.12 | Entorno de servidor local |
| Apache | 2.4.65 | Permite acceder a phpMyAdmin |
| MariaDB | 10.11.16 | Sistema de gestión de base de datos |
| PHP | 8.5.12 | Componente incluido en XAMPP, utilizado por phpMyAdmin |
| phpMyAdmin | 5.2.3 | Administración de la base de datos |
| Python | 3.14.10 | Lenguaje de programación |
| Tkinter | Incluido con Python | Desarrollo de la interfaz gráfica |
| mysql-connector-python | 26.10.0 | Conexión entre Python y MariaDB |

> **Nota:** Las versiones de XAMPP y sus componentes corresponden al paquete de referencia XAMPP 8.5.12. Si se utiliza otra versión, las versiones de PHP, MariaDB y phpMyAdmin pueden variar.

## 1.2. Requisitos de software

| Requisito | Descripción |
|---|---|
| Sistema operativo | Windows 10 o Windows 11 |
| Editor de código | Visual Studio Code |
| Servidor local | XAMPP instalado |
| Lenguaje de programación | Python instalado y agregado al PATH |
| Interfaz gráfica | Tkinter |
| Administrador de base de datos | phpMyAdmin |
| Base de datos | MariaDB proporcionada por XAMPP |
| Extensión de Python | Python de Microsoft para Visual Studio Code |
| Dependencia | mysql-connector-python |

## 1.3. Tecnologías utilizadas

| Tecnología | Aplicación dentro del proyecto |
|---|---|
| Python | Desarrollo de la lógica y funcionalidades del sistema. |
| Tkinter | Creación de ventanas, formularios y tablas. |
| XAMPP | Ejecución local de los servicios de Apache y MariaDB. |
| MariaDB | Almacenamiento y gestión de la información. |
| phpMyAdmin | Creación, importación y administración de la base de datos. |
| PHP | Componente incluido en XAMPP para el funcionamiento de phpMyAdmin. |
| Visual Studio Code | Edición y ejecución del código fuente. |


# 2. BASE DE DATOS

## 2.1. Información general

| Característica | Descripción |
|---|---|
| Nombre de la base de datos | Albergue_Peluchin |
| Tipo de base de datos | Relacional |
| Motor de base de datos | MariaDB |
| Entorno de ejecución | XAMPP |
| Administrador | phpMyAdmin |
| Número de tablas | 17 (más la vista V_Mascota) |
| Código en cada tabla | Todas las tablas tienen la columna `codigo` (por ejemplo PRD-0001, MAS-0001), que el sistema genera automáticamente |

## 2.2. Tablas del sistema

La base de datos está compuesta por las siguientes 17 tablas:

| N.º | Nombre de la tabla | Función general |
|---|---|---|
| 1 | Usuario | Almacena la información de los usuarios del sistema. |
| 2 | Categoria | Organiza los productos por categorías. |
| 3 | Unidad_Medida | Define las unidades utilizadas para los productos. |
| 4 | Especie | Registra las especies de animales (perro, gato...). |
| 5 | Raza | Registra las razas de cada especie. |
| 6 | Producto | Almacena la información de los productos e insumos. |
| 7 | Inventario | Guarda el stock actual y el stock mínimo de cada producto. |
| 8 | Institucion | Registra las instituciones relacionadas con el albergue. |
| 9 | Donante | Registra la información de los donantes. |
| 10 | Donacion | Almacena las donaciones recibidas. |
| 11 | Lote | Permite controlar cantidades y fechas de vencimiento. |
| 12 | Movimiento | Registra las entradas y salidas de inventario (incluidas las entregas). |
| 13 | Detalle_Movimiento | Almacena el detalle de cada movimiento: lote, cantidad, concepto y destinatario. |
| 14 | Mascota | Registra los animales del albergue. |
| 15 | Cuidados_Especiales | Registra los programas de atención especial. |
| 16 | Mascota_Cuidado | Relaciona las mascotas con los cuidados especiales en los que están inscritas. |
| 17 | Beneficiario | Registra lo que recibe cada mascota (categoría, fecha, unidad y cantidad). |

## 2.3. Cambios respecto a la versión anterior

| Cambio | Descripción |
|---|---|
| Columna `codigo` | Se agregó a todas las tablas. |
| Tablas nuevas | Mascota, Inventario, Especie, Raza y Mascota_Cuidado. |
| Beneficiario | Ahora registra el consumo de cada mascota. Los datos de las mascotas pasaron a la tabla Mascota. |
| Programa | Cambió de nombre a Cuidados_Especiales. |
| Programa_Beneficiario | Cambió de nombre a Mascota_Cuidado. |
| Lote | Se eliminó la columna `id_donacion`. Donacion se mantiene como registro aparte. |
| Detalle_Movimiento | Se agregaron las columnas `concepto` (entradas y salidas) y `destinatario` (solo salidas). |
| Entrega | Se eliminó la tabla. Las entregas se registran como Movimiento de tipo SALIDA. |
| Producto | El stock mínimo pasó a la tabla Inventario. |

## 2.4. Administración de la base de datos

La base de datos se administra mediante phpMyAdmin, incluido en XAMPP.

| Componente | Función |
|---|---|
| Apache | Permite acceder a phpMyAdmin desde el navegador. |
| MySQL (XAMPP) | Inicia el servicio MariaDB. |
| MariaDB | Gestiona y almacena los datos del sistema. |
| phpMyAdmin | Permite visualizar, importar y administrar las tablas. |

> **Importante:** No es necesario instalar MySQL Server por separado ni utilizar DBeaver. El servicio de base de datos se inicia directamente desde el módulo MySQL del panel de control de XAMPP.

---

# 3. INSTALACIÓN PASO A PASO – WINDOWS + XAMPP

La siguiente guía describe el procedimiento para preparar el entorno, crear la base de datos y ejecutar el sistema.

## 3.1. Instalación de las herramientas

| Paso | Herramienta | Procedimiento |
|---|---|---|
| 1 | Visual Studio Code | Descargar e instalar Visual Studio Code desde su página oficial. |
| 2 | Extensión Python | Abrir la sección de extensiones e instalar Python de Microsoft. |
| 3 | Python | Descargar Python para Windows, ejecutar el instalador y marcar la opción **Add Python to PATH**. |
| 4 | XAMPP | Descargar XAMPP para Windows e instalar los componentes Apache, MySQL y PHP. |
| 5 | Ubicación | Se recomienda instalar XAMPP en `C:\xampp`. |

## 3.2. Verificar la instalación de Python

Abrir una terminal de Windows o la terminal integrada de Visual Studio Code y ejecutar:

Verificar la versión de Python:

```
py --version
```

Verificar Tkinter:

```
py -m tkinter
```

Si aparece una ventana de prueba, Tkinter está disponible.

## 3.3. Iniciar los servicios de XAMPP

1. Abrir XAMPP Control Panel.
2. Buscar el módulo **Apache** y presionar **Start**.
3. Buscar el módulo **MySQL** y presionar **Start**.
4. Verificar que ambos servicios aparezcan activos.

> **Nota:** El módulo MySQL de XAMPP utiliza MariaDB como motor de base de datos.

## 3.4. Acceder a phpMyAdmin

Abrir el navegador e ingresar a:

```
http://localhost/phpmyadmin
```

Desde esta dirección se podrá administrar la base de datos.

## 3.5. Abrir el proyecto en Visual Studio Code

1. Abrir Visual Studio Code.
2. Seleccionar **Archivo → Abrir carpeta**.
3. Buscar la carpeta del proyecto.
4. Seleccionarla y abrirla.
5. Verificar que aparezcan los archivos Python y las carpetas `Base_de_Datos` e `imagenes`.

## 3.6. Instalar las dependencias

Abrir la terminal integrada de Visual Studio Code y ejecutar:

Actualizar pip:

```
py -m pip install --upgrade pip
```

Instalar las dependencias del proyecto:

```
py -m pip install -r requirements.txt
```

El archivo `requirements.txt` contiene las dependencias necesarias para conectar Python con MariaDB.

## 3.7. Configurar la conexión a la base de datos

Abrir el archivo `conexion.py` y verificar que los datos correspondan a la configuración local de XAMPP.

Ejemplo de conexión:

```python
import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="Albergue_Peluchin",
            port=3306
        )
    except Error as e:
        print("Error de conexión:", e)
        return None
```

| Parámetro | Descripción |
|---|---|
| host | Dirección local del servidor. |
| user | Usuario de MariaDB. |
| password | Contraseña configurada en MariaDB. |
| database | Nombre de la base de datos. |
| port | Puerto de conexión, normalmente 3306. |

> **Importante:** Si el usuario `root` tiene contraseña, se debe colocar en el campo `password`. El nombre de la base de datos debe coincidir exactamente con el creado en el paso siguiente.

## 3.8. Crear la base de datos

Con el módulo MySQL de XAMPP iniciado, existen dos formas de crear la base de datos.

**Opción A (recomendada): con el script del proyecto**

```
py crear_base.py
```

El programa pide el usuario y la contraseña de MySQL, crea la base y las 17 tablas, y ofrece aplicar las mejoras opcionales (regla de vencimiento en Lote y validación del destinatario en los movimientos).

| Situación | Qué hace el script |
|---|---|
| La base no existe | La crea desde cero. |
| La base ya existe | Pregunta si se desea borrarla y crearla de nuevo. **Los datos se pierden.** |

> **Importante:** Si ya se tenía la base con la estructura anterior (tablas Entrega y Programa), se debe usar esta opción para pasar a la estructura nueva.

**Opción B: con phpMyAdmin**

| Paso | Acción | Descripción |
|---|---|---|
| 1 | Ingresar a phpMyAdmin | Abrir `http://localhost/phpmyadmin`. |
| 2 | Seleccionar Importar | Ingresar a la pestaña **Importar**. |
| 3 | Seleccionar archivo | Buscar `Base_de_Datos/albergue_peluchin_inicial_corregida.sql`. |
| 4 | Importar | Presionar **Importar** o **Continuar**. |
| 5 | Verificar | Comprobar que se haya creado la base de datos Albergue_Peluchin. |
| 6 | Comprobar tablas | Verificar que existan las 17 tablas del sistema. |

> **Nota:** Con la opción B no se aplican las mejoras opcionales de `crear_base.py`.

## 3.9. Crear el usuario administrador

Antes de iniciar el sistema por primera vez, ejecutar:

```
py crear_admin.py
```

El programa solicitará los siguientes datos:

| Dato | Descripción |
|---|---|
| Nombre de usuario | Identificador para iniciar sesión. |
| Nombre completo | Nombre del administrador. |
| Contraseña | Clave de acceso de mínimo 8 caracteres. |
| Confirmación | Repetición de la contraseña para verificarla. |

## 3.10. Ejecutar el sistema

Una vez completada la instalación y configuración, ejecutar:

```
py app.py
```

Se abrirá la interfaz gráfica del Sistema de Inventario y Suministros del Albergue de Mascotas Peluchin.

## 3.11. Primeros pasos dentro del sistema

Para que los menús desplegables tengan opciones, se recomienda llenar los datos en este orden:

| Orden | Pantalla | Qué registrar |
|---|---|---|
| 1 | Categorías de productos | Alimento, Medicina, Limpieza... |
| 2 | Unidades de medida | Kilogramo (kg), Bolsa, Dosis... |
| 3 | Especies y Razas | Perro, Gato y sus razas. |
| 4 | Productos | Los productos del albergue, con su stock mínimo. |
| 5 | Mascotas | Los animales que viven en el albergue. |
| 6 | Registrar entrada o salida | Las primeras entradas de productos al inventario. |


# 4. FUNCIONALIDADES DEL SISTEMA

El sistema contempla los siguientes módulos y operaciones:

| Módulo | Funcionalidades |
|---|---|
| Gestión de usuarios | Inicio de sesión, registro, consulta y modificación de usuarios (solo el rol ADMIN). |
| Gestión de productos | Registro, consulta y modificación de productos y de su stock mínimo. |
| Listas de apoyo | Categorías de productos, unidades de medida, especies y razas. |
| Gestión de donaciones | Registro de donantes, instituciones y donaciones. |
| Control de inventario | Registro de entradas y salidas en una sola pantalla. |
| Control de lotes | Seguimiento de cantidades y fechas de vencimiento. |
| Gestión de mascotas | Registro de mascotas, de su ingreso y salida, y de lo que consume cada una. |
| Cuidados especiales | Registro de cuidados especiales e inscripción de mascotas. |
| Reportes y consultas | Existencias, historial de movimientos, alertas y resumen general. |

## 4.1. Control de inventario

| Operación | Descripción |
|---|---|
| Entradas | Cada producto que ingresa crea un lote con su cantidad y fecha de vencimiento (opcional). |
| Salidas | Descuentan primero el lote que vence antes. Los lotes vencidos no se entregan. |
| Concepto | Se registra en entradas y salidas (compra, donación, alimentación, atención veterinaria...). |
| Destinatario | Se registra solo en las salidas (una persona, institución o mascota). |
| Mascota beneficiaria | Si una salida es para una mascota, el consumo queda anotado automáticamente en Beneficiario. |
| Existencias | El Inventario se actualiza solo con cada movimiento. |
| Validación | Comprobación de cantidades disponibles antes de registrar una salida. |
| Stock mínimo | Identificación de productos con existencias bajas. |
| Vencimientos | Consulta de lotes vencidos y de los que vencen en los próximos 30 días. |

## 4.2. Pantallas del sistema

| Sección | Pantallas |
|---|---|
| Inventario | Registrar entrada o salida, Existencias, Lotes y vencimientos, Historial de movimientos, Productos. |
| Mascotas | Mascotas, Consumo por mascota, Cuidados especiales, Inscribir en un cuidado. |
| Donaciones | Donaciones recibidas, Donantes, Instituciones. |
| Listas y usuarios | Categorías de productos, Unidades de medida, Especies, Razas, Usuarios. |
| Reportes | Alertas (stock bajo y vencimientos) y Resumen general. |

## 4.3. Características de la interfaz

| Característica | Descripción |
|---|---|
| Logo del albergue | Se muestra en el inicio de sesión y en todas las pantallas. |
| Botones explicados | Cada botón del inicio indica para qué sirve. |
| Ayuda en pantalla | Cada pantalla tiene un recuadro amarillo que explica qué se hace ahí. |
| Códigos automáticos | El sistema genera el código de cada registro (PRD-0001, MAS-0001...). |
| Campos numéricos | Cantidad, stock mínimo y teléfono solo aceptan números. |
| Buscador | Las listas de registros tienen un cuadro para buscar. |
| Colores de alerta | Las filas en rojo o naranja indican poco stock, lotes por vencer o vencidos. |


# 5. ESTRUCTURA DEL PROYECTO

La estructura principal del proyecto es la siguiente:

```
Albergue_Peluchin_Sistema/
│
├── app.py
├── conexion.py
├── seguridad.py
├── crear_admin.py
├── crear_base.py
├── completar_base.py
├── requirements.txt
├── README.md
├── BITACORA.md
├── Base_de_Datos/
│   └── albergue_peluchin_inicial_corregida.sql
└── imagenes/
    ├── logo_grande.png
    ├── logo_pequeno.png
    └── logo_mini.png

## 5.1. Descripción de los archivos

| Archivo | Descripción |
|---|---|
| app.py | Contiene la interfaz gráfica y las funcionalidades del sistema. |
| conexion.py | Establece la conexión con MariaDB. |
| seguridad.py | Gestiona la protección y verificación de contraseñas. |
| crear_admin.py | Permite crear el primer usuario administrador. |
| crear_base.py | Crea la base de datos desde cero (borra la anterior si existe). |
| completar_base.py | Agrega las tablas que falten sin borrar datos (solo con la estructura nueva). |
| requirements.txt | Contiene las dependencias necesarias para ejecutar el proyecto. |
| Base_de_Datos/ | Contiene el script SQL de la base de datos. |
| imagenes/ | Contiene el logo del albergue que se muestra en la interfaz. |
| BITACORA.md | Registro del trabajo colaborativo del equipo. |


# 6. SOLUCIÓN DE PROBLEMAS

| Problema | Posible causa | Solución |
|---|---|---|
| Error de conexión con la base de datos | MySQL de XAMPP no está iniciado. | Abrir XAMPP e iniciar el módulo MySQL. |
| Error de conexión en el puerto 3306 | Puerto incorrecto o servicio detenido. | Comprobar el puerto configurado en XAMPP y en `conexion.py`. |
| No abre phpMyAdmin | Apache está detenido. | Iniciar Apache desde XAMPP. |
| No encuentra la base de datos | Nombre incorrecto o base de datos no creada. | Revisar el nombre y ejecutar `py crear_base.py`. |
| Error «Table doesn't exist» o «Unknown column» | La base tiene la estructura anterior. | Ejecutar `py crear_base.py` para crear la estructura nueva. |
| Error de mysql.connector | Dependencia no instalada. | Ejecutar `py -m pip install mysql-connector-python`. |
| Los menús desplegables están vacíos | Faltan datos en las listas de apoyo. | Llenar categorías, unidades, especies y razas (ver 3.11). |
| No aparece el logo | Falta la carpeta `imagenes`. | Verificar que `imagenes/` esté junto a `app.py`. |
| Error al ejecutar la aplicación | Terminal ubicada en otra carpeta o error de código. | Abrir la carpeta del proyecto y ejecutar `py app.py`. |

## 6.1. Comandos útiles

| Comando | Función |
|---|---|
| `py --version` | Consultar la versión de Python. |
| `py -m tkinter` | Comprobar Tkinter. |
| `py -m pip install -r requirements.txt` | Instalar las dependencias. |
| `py crear_base.py` | Crear la base de datos desde cero. |
| `py crear_admin.py` | Crear el usuario administrador. |
| `py app.py` | Ejecutar el sistema. |


# 7. CONSIDERACIONES IMPORTANTES

| Elemento | Consideración |
|---|---|
| XAMPP | Debe estar iniciado antes de utilizar el sistema. |
| Apache | Se utiliza para acceder a phpMyAdmin. |
| MariaDB | Se inicia desde el módulo MySQL de XAMPP. |
| Python | Ejecuta la aplicación de escritorio. |
| Tkinter | Permite mostrar la interfaz gráfica. |
| phpMyAdmin | Permite administrar la base de datos. |
| crear_base.py | Borra los datos si la base ya existe. Usarlo con cuidado. |
| DBeaver | No se utiliza en este proyecto. |
| MySQL Server | No es necesario instalarlo por separado. |
| Base de datos local | Cada instalación local utiliza su propia base de datos, salvo que se configure un servidor compartido. |
| Credenciales | No se deben publicar contraseñas reales ni datos privados en GitHub. |


# 8. CRÉDITOS

| Información | Detalle |
|---|---|
| Nombre del proyecto | Sistema de Inventario y Suministros del Albergue de Mascotas Peluchin |
| Identificación | F5.exe |
| Grupo | Grupo 3 |
| Lenguaje de programación | Python |
| Interfaz gráfica | Tkinter |
| Base de datos | MariaDB |
| Entorno local | XAMPP |
| Administración de base de datos | phpMyAdmin |
| Editor de código | Visual Studio Code |
| Control de versiones | Git y GitHub |

**Objetivo del proyecto:** Facilitar la administración y el control de los productos, donaciones y suministros destinados al cuidado de las mascotas del Albergue Peluchin.
