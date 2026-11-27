# Bitácora del Proyecto — Sistema Albergue Peluchín

## **TRABAJO COLABORATIVO — 12/11/2026**

- Creación del repositorio en GitHub
- Creación del archivo README.md
- Creación del archivo BITACORA.md
- Diseño preliminar de la interfaz gráfica del sistema

---

## **TRABAJO COLABORATIVO — 15/11/2026**

- Establecimiento de conexión entre la base de datos y la interfaz gráfica del sistema
- Elaboración del Documento de Diagnóstico "AS-IS" y documento de Requerimientos del sistema
- Limpieza y edición de contenido duplicado en el archivo README.md

---

## **TRABAJO COLABORATIVO — 19/11/2026**

- Creación de la carpeta "Base de Datos" dentro de la estructura del proyecto
- Organización e implementación de los archivos con código SQL en la carpeta correspondiente

### **Segunda sesión de trabajo — 19/11/2026**

- Actualización y mejora del funcionamiento general de todas las ventanas del sistema
- Actualización del archivo README.md conforme a las indicaciones recibidas por el Ing. Rubén Soria
- Verificación de operaciones CRUD: comprobación de que el sistema pueda agregar, modificar y eliminar registros desde la interfaz hacia la base de datos de forma simultánea y correcta

---

## **TRABAJO COLABORATIVO — 20/11/2026**

### **Modificaciones en Base de Datos**
- Actualización de la estructura: creación de las nuevas tablas Mascota, Inventario, Especie y Raza
- Revisión e incorporación de código en todas las tablas existentes
- Cambio de denominación: Programas pasa a denominarse Cuidados_Especiales
- Eliminación del módulo o ventana denominada Entrega
- Modificación en tabla Lote: eliminación del campo id_donacion

### **Interfaz Gráfica**
- Rediseño general de la interfaz gráfica del sistema
- Incorporación del logo del Albergue Peluchín en la interfaz
- Unificación de vistas: diseño de una pantalla única para la gestión de entradas y salidas

### **Recursos Visuales**
- Inclusión de imágenes reales del Albergue Peluchín dentro de la interfaz del sistema

### **Validación de Datos**
- Revisión completa de las reglas de validación de datos en campos y formularios de ingreso
- Corrección de mensajes de error y advertencias
- Pruebas de integridad de los datos ingresados al sistema

---

## **TRABAJO COLABORATIVO — 25/11/2026**
- Sistematización de datos en el sistema
- Verificación de ventanas funcionales y alertas
- Conexión LAN 

---

## **TRABAJO COLABORATIVO — 26/11/2026**

### **Validación de Datos**
- La fecha de nacimiento de la mascota ya no acepta fechas futuras (antes la edad salía -1)
- La fecha de ingreso de la mascota no puede ser futura ni anterior al nacimiento
- La fecha de salida no puede ser anterior al nacimiento ni al ingreso
- Los nombres ya no pueden ser solo números (productos, categorías, donantes, instituciones...)
- Nombres de mascota, especie, raza y usuario: solo letras (el campo no deja escribir números)
- Teléfonos: solo números, de 7 u 8 dígitos (el campo no deja escribir más de 8)

### **Modificaciones en Base de Datos**
- Reglas CHECK con nombre para nombres, teléfonos y orden de fechas de la mascota
- Teléfonos de Donante e Institucion pasan a VARCHAR(8)
- Triggers trg_mascota_fechas_ins / trg_mascota_fechas_upd para impedir fechas futuras
- Nuevo script aplicar_restricciones.py para actualizar bases existentes sin perder datos

### **Revisión completa de validaciones**
- Teléfono: el límite de 8 dígitos ahora se aplica sobre el contenido del campo (al escribir, pegar o cargar un registro), no solo sobre la tecla presionada
- Todos los campos de texto tienen el largo máximo de su columna en la base
- Cantidades: hasta 999999.99 y máximo 2 decimales
- Fechas entre 1990 y 2099; no futuras en donaciones, lotes, consumos e inscripciones
- Consumos e inscripciones solo dentro de la estadía de la mascota
- La raza de la mascota debe pertenecer a su especie
- Donante PERSONA/INSTITUCION controlado también en la base
- No se pueden ingresar productos ya vencidos
- Nombre de usuario sin espacios; destino, concepto, destinatario y tipo de institución con letras
- Las reglas de vencimiento del lote y del destinatario pasan a ser obligatorias (ya no opcionales)
- Nuevo módulo validaciones.py con las reglas compartidas

### **Pantalla «Cálculo de las alertas**
- Se integró el modelo matemático (Subproducto P2) al sistema, junto al botón de Alertas
- Usa los datos reales de la base: E y D del período elegido, m del inventario, I = existencia de hoy − E + D
- Resuelve paso a paso: balance F = I + E − D, restricción F ≥ 0, alerta de stock mínimo y alerta de vencimiento
- Sus resultados coinciden con la pantalla «Alertas» (stock vigente, m > 0, k = 30 días)
- Acceso desde el inicio y desde la pantalla de Alertas

### **Buscador**
- Debajo de la caja de búsqueda se indica por qué atributos busca cada pantalla (ej. «Busca por: código o nombre del producto»)
- La búsqueda solo mira esos atributos (antes miraba todas las columnas: «10» traía productos con stock 10)
- Muestra cuántos resultados hay, o «Sin resultados» en rojo
- Usuarios: las columnas se llaman «Usuario» y «Nombre completo» (antes ambas decían «Nombre»)

---

## **TRABAJO COLABORATIVO — 27/11/2026** 

### **Corrección Base de Datos y Diagrama E-R**
- Se elimino la tabla V_Mascotas
- Se modifico la en base al diagrama E-R
- Cambio de formato de fecha AAAA/MM/DD a DD/MM/AAA
- Creación de botón calendario   

