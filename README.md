# GRUPO 3 
# SISTEMA DE INVENTARIO Y SUMINISTROS 
Lo que nuestro equipo busca crear es un sistema de inventario y suministros que apoye a tener una mejor organizacion con lo suministros y el inventario de un albergue, para implementar esta idea tras un breve estudio e investigacion, tomamos en cuenta el "Albergue Peluchin".
El Albergue Peluchín no cuenta con un sistema de inventario, por lo que el registro de alimentos e insumos, las donaciones recibidas y su entrega a los beneficiarios se llevan sin un control organizado. Esto provoca desorden, pérdida de recursos y dificultades para dar seguimiento a las actividades de asistencia. 
# OBJETIVO GENERAL
Nuestro obejtivo como equipo es desarrollar un sistema de inventario y suministros para el Albergue Peluchín que permita controlar los alimentos e insumos, gestionar las donaciones, dar seguimiento a los programas de asistencia y facilitar el intercambio de información con otras instituciones, evitando la pérdida de recursos y mejorando su uso.
# INTEGRANTES

| N° | Nombre completo | Rol | GitHub |
|---|---|---|---|
| 1 | Medinaceli Andrade Fernando Yeray  | Lider | @Fma748 |
| 2 | Mamani Quispe Elvis | Lider de documentos | @BiscochoTK|
| 3 | Apaza Nistaza David Abraham | Developer | @DavidNistaza07-pixel
| 4 | Magueño Cano Benjamin  | Developer | @maguenobenjamin-maker| 
5 | Nina Garcia Hugo Marcelo  | Publicista | @Cannzert

Descripción

El proyecto **F5.exe – Sistema de Inventario y Suministros Albergue Peluchín** consiste en el desarrollo de un programa informático orientado a mejorar el registro, la organización y el control de los alimentos, insumos y donaciones del albergue.

El sistema busca facilitar el manejo de la información mediante funcionalidades que permitan registrar productos, controlar sus cantidades disponibles, gestionar sus entradas y salidas, identificar productos próximos a vencer y realizar un seguimiento de las donaciones recibidas.

Asimismo, contempla el registro de los recursos destinados a los programas de asistencia, permitiendo mantener una mejor organización de la información y contribuir a una distribución más ordenada de los suministros.


## Tecnologías

El sistema es una aplicación de escritorio hecha en Python que guarda su información en una base de datos MariaDB. XAMPP se usa únicamente para levantar esa base de datos en la computadora local y administrarla desde el navegador.

| Tecnología | Para qué se usa en el proyecto |
|---|---|
| **Python** | Lógica del sistema. |
| **Tkinter** | Ventanas, formularios y tablas de la interfaz gráfica. Viene incluido con Python. |
| **XAMPP** | Entorno local que ejecuta Apache y MariaDB. |
| **MariaDB** | Almacenamiento de la información. En XAMPP aparece como módulo **MySQL**. |
| **Apache** | Servidor web que permite abrir phpMyAdmin. La aplicación en sí no lo necesita. |
| **phpMyAdmin** | Importación y administración de la base de datos desde el navegador. |
| **mysql-connector-python** | Conexión entre Python y MariaDB. |
| **Visual Studio Code** | Edición y ejecución del código fuente. |
| **Git y GitHub** | Control de versiones y alojamiento del repositorio. |

### Cómo se relacionan

```
app.py (Python + Tkinter)
        │  mysql-connector-python
        ▼
MariaDB  ←  módulo "MySQL" de XAMPP, puerto 3306
        ▲
        │  administración
phpMyAdmin  ←  módulo "Apache" de XAMPP, http://localhost/phpmyadmin
```

- Para **usar el sistema** basta con que el módulo **MySQL** de XAMPP esté iniciado.
- Para **administrar la base de datos** con phpMyAdmin se necesita además el módulo **Apache**.
- No se instala MySQL Server por separado ni se utiliza DBeaver.

---

## 1. Requisitos

### Versiones de referencia

| Herramienta | Versión | Función |
|---|---|---|
| Visual Studio Code | Estable | Editor de código |
| XAMPP | 8.5.12 | Entorno de servidor local |
| Apache | 2.4.65 | Permite acceder a phpMyAdmin |
| MariaDB | 10.11.16 | Sistema de gestión de base de datos |
| PHP | 8.5.12 | Incluido en XAMPP; lo utiliza phpMyAdmin |
| phpMyAdmin | 5.2.3 | Administración de la base de datos |
| Python | 3.14.10 | Lenguaje de programación |
| Tkinter | Incluido con Python | Interfaz gráfica |
| mysql-connector-python | 26.10.0 | Conexión entre Python y MariaDB |

> **Importante:** las versiones de Apache, MariaDB, PHP y phpMyAdmin corresponden al paquete XAMPP 8.5.12. Con otra versión de XAMPP pueden variar, y el sistema debería funcionar igual.

### Antes de empezar

- Windows 10 o Windows 11.
- Permisos para instalar programas en el equipo.
- La carpeta del proyecto `Albergue_Peluchin_Sistema`.
- El archivo de base de datos `albergue_peluchin_inicial_corregida.sql`.

---

## 2. Instalación paso a paso (Windows + XAMPP)

Resumen del recorrido:

1. Instalar Visual Studio Code
2. Instalar XAMPP
3. Iniciar Apache y MySQL
4. Abrir phpMyAdmin
5. Importar la base de datos
6. Instalar Python
7. Abrir el proyecto
8. Instalar las dependencias
9. Configurar la conexión
10. Crear el usuario administrador
11. Ejecutar el sistema

Los pasos 1 al 10 se hacen una sola vez. Para el uso diario, ver [Uso diario](#3-uso-diario).

### Paso 1. Instalar Visual Studio Code

1. Descargar Visual Studio Code desde su página oficial: <https://code.visualstudio.com>
2. Ejecutar el instalador y completar la instalación.
3. Abrir Visual Studio Code.
4. Ir a la sección **Extensiones** (`Ctrl + Shift + X`).
5. Buscar **Python** e instalar la extensión desarrollada por **Microsoft**.

### Paso 2. Instalar XAMPP

1. Descargar XAMPP para Windows desde <https://www.apachefriends.org>
2. Ejecutar el instalador.
3. En la selección de componentes, dejar marcados como mínimo **Apache**, **MySQL**, **PHP** y **phpMyAdmin**.
4. Instalar en la ubicación por defecto:

   ```
   C:\xampp
   ```

5. Finalizar la instalación.

> Conviene mantener la ruta `C:\xampp`. Instalar XAMPP dentro de `C:\Program Files` suele dar problemas de permisos.

### Paso 3. Iniciar los servicios de XAMPP

1. Abrir **XAMPP Control Panel**.
2. En la fila **Apache**, presionar **Start**.
3. En la fila **MySQL**, presionar **Start**.

**Resultado esperado:** los nombres de ambos módulos quedan resaltados en verde y se muestran sus puertos (Apache: 80 y 443; MySQL: 3306).

> El módulo se llama **MySQL**, pero el motor que ejecuta es **MariaDB**. Es el comportamiento normal de XAMPP.

Si alguno no inicia, revisar [Apache o MySQL no inician](#apache-o-mysql-no-inician-en-xampp).

### Paso 4. Abrir phpMyAdmin

1. Abrir el navegador.
2. Ingresar a:

   ```
   http://localhost/phpmyadmin
   ```

**Resultado esperado:** se abre el panel de phpMyAdmin, con la lista de bases de datos en la columna izquierda.

### Paso 5. Importar la base de datos

1. En phpMyAdmin, seleccionar la pestaña **Importar** del menú superior (sin entrar antes a ninguna base de datos).
2. Presionar **Seleccionar archivo**.
3. Buscar el archivo SQL del proyecto:

   ```
   albergue_peluchin_inicial_corregida.sql
   ```

4. Presionar **Importar** (o **Continuar**, según la versión) al final de la página.
5. Esperar el mensaje de importación finalizada.

**Resultado esperado:** en la columna izquierda aparece la base de datos `Albergue_Peluchin` con sus **14 tablas**:

| | | |
|---|---|---|
| Usuario | Categoria | Unidad_Medida |
| Producto | Institucion | Donante |
| Donacion | Lote | Movimiento |
| Detalle_Movimiento | Programa | Beneficiario |
| Programa_Beneficiario | Entrega | |

> En Windows, phpMyAdmin puede mostrar los nombres en minúsculas (`albergue_peluchin`, `usuario`, etc.). Es normal y no afecta al sistema.

### Paso 6. Instalar Python

1. Descargar Python para Windows desde <https://www.python.org/downloads/>
2. Ejecutar el instalador.
3. **Marcar la casilla "Add Python to PATH"** antes de continuar. Sin ella, los comandos de los pasos siguientes no funcionarán.
4. Completar la instalación.
5. Abrir una terminal de Windows o la de Visual Studio Code y comprobar la instalación:

   ```
   py --version
   ```

   Debe mostrar la versión instalada, por ejemplo `Python 3.14.10`.

6. Comprobar que Tkinter esté disponible:

   ```
   py -m tkinter
   ```

   **Resultado esperado:** se abre una pequeña ventana de prueba. Cerrarla para continuar.

### Paso 7. Abrir el proyecto en Visual Studio Code

Si el proyecto está en GitHub, primero clonarlo:

```
git clone <URL-del-repositorio>
```

Luego:

1. Abrir Visual Studio Code.
2. Seleccionar **Archivo → Abrir carpeta**.
3. Elegir la carpeta `Albergue_Peluchin_Sistema`.

**Resultado esperado:** en el explorador de archivos aparecen `app.py`, `conexion.py`, `seguridad.py`, `crear_admin.py`, `requirements.txt` y `LEEME.txt`.

### Paso 8. Instalar las dependencias

1. Abrir la terminal integrada: **Terminal → Nueva terminal** (`` Ctrl + ` ``).
2. Verificar que la terminal esté ubicada en la carpeta del proyecto.
3. Actualizar pip:

   ```
   py -m pip install --upgrade pip
   ```

4. Instalar las dependencias:

   ```
   py -m pip install -r requirements.txt
   ```

El archivo `requirements.txt` contiene `mysql-connector-python`, la librería que conecta Python con MariaDB.

**Resultado esperado:** la terminal termina con un mensaje `Successfully installed ...`.

### Paso 9. Configurar la conexión a la base de datos

1. Abrir el archivo `conexion.py`.
2. Verificar que los datos coincidan con la configuración local de XAMPP:

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

| Parámetro | Significado | Valor en una instalación nueva de XAMPP |
|---|---|---|
| `host` | Dirección del servidor de base de datos | `localhost` |
| `user` | Usuario de MariaDB | `root` |
| `password` | Contraseña de ese usuario | vacía (`""`) |
| `database` | Nombre de la base de datos | `Albergue_Peluchin` |
| `port` | Puerto de conexión | `3306` |

> Si al usuario `root` se le asignó una contraseña, o si MySQL se inició en otro puerto (por ejemplo 3307), esos valores deben actualizarse aquí.

### Paso 10. Crear el usuario administrador

Antes de iniciar el sistema por primera vez, con el módulo **MySQL** de XAMPP iniciado, ejecutar:

```
py crear_admin.py
```

El programa pedirá:

- Nombre de usuario.
- Nombre completo.
- Contraseña (mínimo **8 caracteres**).

Con estos datos se iniciará sesión en el sistema. Este paso se realiza una sola vez por instalación.

### Paso 11. Ejecutar el sistema

```
py app.py
```

**Resultado esperado:** se abre la ventana de inicio de sesión del Sistema de Inventario y Suministros del Albergue de Mascotas Peluchin. Ingresar con el usuario administrador creado en el paso anterior.

---

## 3. Uso diario

Una vez instalado, para levantar el sistema solo hace falta:

1. Abrir **XAMPP Control Panel** e iniciar **MySQL**.
2. Abrir la carpeta del proyecto en Visual Studio Code.
3. Ejecutar en la terminal:

   ```
   py app.py
   ```

Apache solo debe iniciarse cuando se quiera entrar a phpMyAdmin.

Al terminar, cerrar la aplicación y presionar **Stop** en los módulos activos de XAMPP.

---

## 4. Funcionalidades del sistema

| Módulo | Operaciones |
|---|---|
| **Usuarios** | Inicio de sesión, registro, consulta y modificación de usuarios. |
| **Productos** | Registro, consulta y modificación de productos; gestión de categorías y unidades de medida. |
| **Donaciones** | Registro de donantes e instituciones; registro y consulta de donaciones. |
| **Inventario** | Entradas mediante lotes, salidas de productos, actualización de existencias, validación de cantidades disponibles, alertas de stock mínimo y consulta de lotes próximos a vencer. |
| **Mascotas y programas** | Registro, consulta y modificación de mascotas beneficiarias; registro de programas e inscripción de mascotas en programas. |
| **Reportes y consultas** | Consulta general del inventario, resumen de existencias, alertas de productos y consulta de movimientos. |

---

## 5. Estructura del proyecto

```
Albergue_Peluchin_Sistema/
│
├── app.py
├── conexion.py
├── seguridad.py
├── crear_admin.py
├── requirements.txt
└── LEEME.txt
```

| Archivo | Descripción |
|---|---|
| `app.py` | Interfaz gráfica y funcionalidades del sistema. Es el archivo que se ejecuta. |
| `conexion.py` | Establece la conexión con MariaDB. |
| `seguridad.py` | Protección y verificación de contraseñas. |
| `crear_admin.py` | Crea el primer usuario administrador. |
| `requirements.txt` | Lista de dependencias. |
| `LEEME.txt` | Información básica del proyecto. |

---

## 6. Solución de problemas

### Apache o MySQL no inician en XAMPP

Casi siempre se debe a que otro programa ocupa el puerto.

- **Apache (puertos 80 / 443):** cerrar programas que los usen (IIS, Skype, otro servidor web) y volver a presionar **Start**.
- **MySQL (puerto 3306):** si hay un MySQL Server instalado aparte, detener ese servicio desde **Servicios** de Windows, o cambiar el puerto de XAMPP y actualizar `port` en `conexion.py`.
- El botón **Netstat** del panel de XAMPP muestra qué programa ocupa cada puerto, y **Logs** muestra el detalle del error.

### Error de conexión con la base de datos

1. Verificar que XAMPP esté abierto y el módulo **MySQL** iniciado.
2. Confirmar en phpMyAdmin que exista la base de datos `Albergue_Peluchin`.
3. Revisar `user` y `password` en `conexion.py`.
4. Comprobar que `port` coincida con el puerto que muestra XAMPP junto a MySQL.

### No abre phpMyAdmin

1. Verificar que **Apache** y **MySQL** estén iniciados.
2. Ingresar a `http://localhost/phpmyadmin`.
3. Si Apache usa otro puerto (por ejemplo 8080), ingresar a `http://localhost:8080/phpmyadmin`.

### Error al importar el archivo SQL

- Si aparece **"No database selected"**: crear primero una base de datos llamada `Albergue_Peluchin` (pestaña **Bases de datos**), entrar en ella e importar el archivo desde allí.
- Si indica que la base de datos o las tablas **ya existen**: ya fue importada antes. Para reimportar desde cero, eliminar la base de datos y repetir el Paso 5 (se pierden los datos registrados).

### `py` no se reconoce como comando

Python no quedó agregado al PATH. Reinstalarlo marcando **Add Python to PATH** y abrir una terminal nueva.

### Error de módulo `mysql.connector`

```
py -m pip install mysql-connector-python
```

### Error al ejecutar la aplicación

Comprobar que la terminal esté ubicada en la carpeta del proyecto (donde está `app.py`) y ejecutar:

```
py app.py
```

### No se puede iniciar sesión

Verificar que se haya ejecutado `py crear_admin.py` (Paso 10) y que se estén usando el usuario y la contraseña registrados allí.

---

## 7. Consideraciones importantes

- El módulo **MySQL** de XAMPP debe estar iniciado antes de usar el sistema.
- Apache solo se necesita para acceder a phpMyAdmin.
- No se utiliza DBeaver ni se instala MySQL Server por separado.
- Cada instalación local utiliza su propia base de datos, salvo que se configure un servidor compartido. Los datos registrados en una computadora no aparecen en otra.
- La configuración por defecto de XAMPP (usuario `root` sin contraseña) está pensada para desarrollo local; no debe exponerse a internet sin protegerla.
- Para respaldar la información, usar la pestaña **Exportar** de phpMyAdmin sobre la base de datos `Albergue_Peluchin`.
