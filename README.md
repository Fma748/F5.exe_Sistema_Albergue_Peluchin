
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


1. REQUISITOS

Para instalar y ejecutar el proyecto se necesitan las siguientes herramientas:

Herramienta

Versión de referencia

Función

Visual Studio Code

Versión estable

Editor de código

XAMPP

8.5.12

Entorno de servidor local

Apache

2.4.65

Permite acceder a phpMyAdmin

MariaDB

10.11.16

Sistema de gestión de base de datos

PHP

8.5.12

Componente incluido en XAMPP, utilizado por phpMyAdmin

phpMyAdmin

5.2.3

Administración de la base de datos

Python

3.14.10

Lenguaje de programación

Tkinter

Incluido con Python

Desarrollo de la interfaz gráfica

mysql-connector-python

26.10.0

Conexión entre Python y MariaDB

Importante: Las versiones de XAMPP y sus componentes corresponden al paquete de referencia XAMPP 8.5.12. Si se utiliza otra versión de XAMPP, las versiones de PHP, MariaDB y phpMyAdmin pueden variar.

Requisitos de software

Sistema operativo Windows 10 o Windows 11.

Visual Studio Code instalado.

XAMPP instalado.

Python instalado y agregado al PATH.

Extensión Python de Microsoft en Visual Studio Code.

Base de datos del proyecto.

Dependencia mysql-connector-python.

Tecnologías utilizadas

Python: desarrollo de la lógica del sistema.

Tkinter: creación de ventanas, formularios y tablas.

XAMPP: entorno local para ejecutar los servicios de Apache y MariaDB.

MariaDB: almacenamiento de la información.

phpMyAdmin: creación, importación y administración de la base de datos.

Visual Studio Code: edición y ejecución del código fuente.

2. BASE DE DATOS

Nombre de la base de datos

Albergue_Peluchin

Tablas del sistema

La base de datos está compuesta por 14 tablas:

Usuario

Categoria

Unidad_Medida

Producto

Institucion

Donante

Donacion

Lote

Movimiento

Detalle_Movimiento

Programa

Beneficiario

Programa_Beneficiario

Entrega

Administración de la base de datos

La base de datos se administra mediante phpMyAdmin, que se encuentra incluido en XAMPP.

No es necesario instalar MySQL Server ni utilizar DBeaver. El servicio de base de datos se inicia directamente desde el panel de control de XAMPP, en el módulo llamado MySQL.

3. INSTALACIÓN PASO A PASO – WINDOWS + XAMPP

Paso 1. Instalar Visual Studio Code

Descargar Visual Studio Code desde su página oficial.

Ejecutar el instalador.

Completar la instalación.

Abrir Visual Studio Code.

Ingresar a la sección de extensiones.

Buscar e instalar la extensión Python, desarrollada por Microsoft.

Paso 2. Instalar XAMPP

Descargar XAMPP para Windows.

Ejecutar el instalador.

Seleccionar los componentes necesarios, incluyendo Apache, MySQL y PHP.

Instalar XAMPP en la siguiente ubicación:

C:\xampp

Finalizar la instalación.

Paso 3. Iniciar los servicios de XAMPP

Abrir el XAMPP Control Panel.

Buscar el módulo Apache y presionar Start.

Buscar el módulo MySQL y presionar Start.

Verificar que ambos servicios aparezcan activos.

Nota: El módulo MySQL de XAMPP utiliza MariaDB como motor de base de datos.

Paso 4. Abrir phpMyAdmin

Abrir el navegador.

Ingresar a la siguiente dirección:

http://localhost/phpmyadmin

Se abrirá phpMyAdmin.

Desde esta herramienta se podrá importar y administrar la base de datos.

Paso 5. Importar la base de datos

Ingresar a phpMyAdmin.

Seleccionar la pestaña Importar.

Presionar Seleccionar archivo.

Buscar el archivo SQL del proyecto:

albergue_peluchin_inicial_corregida.sql

Presionar Importar o Continuar.

Esperar a que finalice el proceso.

Verificar que aparezca la base de datos Albergue_Peluchin.

Comprobar que existan las 14 tablas.

Paso 6. Instalar Python

Descargar Python para Windows.

Ejecutar el instalador.

Marcar la opción Add Python to PATH.

Continuar con la instalación.

Abrir una terminal de Windows o la terminal de Visual Studio Code.

Comprobar que Python esté instalado:

py --version

Comprobar que Tkinter esté disponible:

py -m tkinter

Si aparece una ventana de prueba, Tkinter está funcionando correctamente.

Paso 7. Abrir el proyecto en Visual Studio Code

Abrir Visual Studio Code.

Seleccionar Archivo → Abrir carpeta.

Buscar la carpeta del proyecto.

Seleccionarla y abrirla.

Verificar que aparezcan los archivos del sistema.

Paso 8. Instalar las dependencias

Abrir la terminal integrada de Visual Studio Code.

Ejecutar:

py -m pip install --upgrade pip

Después, instalar las dependencias:

py -m pip install -r requirements.txt

El archivo requirements.txt contiene la dependencia necesaria para conectar Python con MariaDB.

Paso 9. Configurar la conexión a la base de datos

Abrir el archivo:

conexion.py

Verificar que los datos de conexión correspondan a la configuración local de XAMPP.

Ejemplo:

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

Importante:

host: dirección local del servidor.

user: usuario de MariaDB.

password: contraseña configurada en MariaDB.

database: nombre de la base de datos.

port: puerto de conexión, normalmente 3306.

Si el usuario root tiene contraseña, se debe colocar en el campo password.

Paso 10. Crear el usuario administrador

Antes de iniciar el sistema por primera vez, ejecutar:

py crear_admin.py

El programa solicitará los datos necesarios para registrar al primer administrador.

Se debe ingresar:

Nombre de usuario.

Nombre completo.

Contraseña.

La contraseña debe tener como mínimo 8 caracteres.

Paso 11. Ejecutar el sistema

Una vez completada la instalación y configuración, ejecutar:

py app.py

Se abrirá la interfaz gráfica del Sistema de Inventario y Suministros del Albergue de Mascotas Peluchin.

4. FUNCIONALIDADES DEL SISTEMA

El sistema permite realizar las siguientes operaciones:

Gestión de usuarios

Inicio de sesión.

Registro de usuarios.

Consulta y modificación de usuarios.

Gestión de productos

Registro de productos.

Consulta de productos.

Modificación de información.

Gestión de categorías y unidades de medida.

Gestión de donaciones

Registro de donantes.

Registro de instituciones.

Registro y consulta de donaciones.

Control de inventario

Registro de entradas mediante lotes.

Registro de salidas de productos.

Actualización de existencias.

Validación de cantidades disponibles.

Alertas de stock mínimo.

Consulta de lotes próximos a vencer.

Gestión de mascotas y programas

Registro de mascotas beneficiarias.

Consulta y modificación de información.

Registro de programas.

Inscripción de mascotas en programas.

Reportes y consultas

Consulta general del inventario.

Resumen de existencias.

Alertas de productos.

Consulta de movimientos.

5. ESTRUCTURA DEL PROYECTO

La estructura principal del proyecto es la siguiente:

Albergue_Peluchin_Sistema/
│
├── app.py
├── conexion.py
├── seguridad.py
├── crear_admin.py
├── requirements.txt
└── LEEME.txt

Descripción de los archivos

Archivo

Descripción

app.py

Contiene la interfaz gráfica y las funcionalidades del sistema.

conexion.py

Establece la conexión con MariaDB.

seguridad.py

Gestiona la protección y verificación de contraseñas.

crear_admin.py

Permite crear el primer usuario administrador.

requirements.txt

Contiene las dependencias necesarias.

LEEME.txt

Contiene información básica del proyecto.

6. SOLUCIÓN DE PROBLEMAS

Error de conexión con la base de datos

Si aparece un error de conexión:

Verificar que XAMPP esté abierto.

Comprobar que el módulo MySQL esté iniciado.

Revisar el nombre de la base de datos.

Verificar el usuario y contraseña en conexion.py.

Comprobar que el puerto sea el correcto.

No abre phpMyAdmin

Verificar que Apache esté iniciado.

Abrir el navegador.

Ingresar a http://localhost/phpmyadmin.

Error de módulo mysql.connector

Ejecutar en la terminal:

py -m pip install mysql-connector-python

Error al ejecutar la aplicación

Comprobar que se está ubicado en la carpeta del proyecto y ejecutar:

py app.py

7. CONSIDERACIONES IMPORTANTES

XAMPP debe estar iniciado antes de utilizar el sistema.

Apache se utiliza para acceder a phpMyAdmin.

MariaDB se inicia desde el módulo MySQL de XAMPP.

Python ejecuta la aplicación de escritorio.

Tkinter permite mostrar la interfaz gráfica.

phpMyAdmin permite administrar la base de datos.

No se utiliza DBeaver.

No se necesita instalar MySQL Server por separado.

Cada instalación local utiliza su propia base de datos, salvo que se configure un servidor compartido.