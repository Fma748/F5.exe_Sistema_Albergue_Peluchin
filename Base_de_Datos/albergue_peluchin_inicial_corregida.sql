-- =====================================================
-- Albergue Peluchin - Inventario y suministros
-- Base de datos actualizada (17 tablas + 1 vista)
-- Cambios respecto a la version anterior:
--   * Todas las tablas tienen la columna "codigo"
--   * Nuevas: Mascota, Inventario, Especie, Raza, Mascota_Cuidado
--   * Beneficiario ahora registra el consumo de cada mascota
--   * Programa pasa a llamarse Cuidados_Especiales
--   * Lote ya no tiene id_donacion
--   * Detalle_Movimiento tiene concepto y destinatario
--   * Se elimina la tabla Entrega (todo se maneja en Movimiento)
-- Requiere MySQL 8.0.16 o MariaDB 10.5 o superior (para que los CHECK se apliquen)
-- =====================================================

CREATE DATABASE IF NOT EXISTS Albergue_Peluchin
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE Albergue_Peluchin;

-- CREACION DE LAS TABLAS

-- -----------------------------------------------------
-- Usuarios del sistema (inicio de sesion y tipo de usuario)
-- -----------------------------------------------------
CREATE TABLE Usuario (
    id_usuario      INT AUTO_INCREMENT PRIMARY KEY,
    codigo          VARCHAR(20) NOT NULL UNIQUE,
    nombre_usuario  VARCHAR(50) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,      -- guardar el hash, nunca la contrasena en texto plano
    nombre_completo VARCHAR(120) NOT NULL,
    rol             ENUM('ADMIN','OPERADOR') NOT NULL DEFAULT 'OPERADOR',
    activo          BOOLEAN NOT NULL DEFAULT TRUE
);

-- -----------------------------------------------------
-- Listas de apoyo (alimentan los menus desplegables)
-- -----------------------------------------------------
CREATE TABLE Categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    codigo       VARCHAR(20) NOT NULL UNIQUE,
    nombre       VARCHAR(100) NOT NULL UNIQUE,
    descripcion  VARCHAR(200)
);

CREATE TABLE Unidad_Medida (
    id_unidad   INT AUTO_INCREMENT PRIMARY KEY,
    codigo      VARCHAR(20) NOT NULL UNIQUE,
    nombre      VARCHAR(50) NOT NULL UNIQUE,
    abreviatura VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE Especie (
    id_especie INT AUTO_INCREMENT PRIMARY KEY,
    codigo     VARCHAR(20) NOT NULL UNIQUE,
    nombre     VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Raza (
    id_raza    INT AUTO_INCREMENT PRIMARY KEY,
    codigo     VARCHAR(20) NOT NULL UNIQUE,
    nombre     VARCHAR(80) NOT NULL,
    id_especie INT NOT NULL,

    FOREIGN KEY (id_especie)
        REFERENCES Especie(id_especie),

    UNIQUE (nombre, id_especie)
);

-- -----------------------------------------------------
-- Productos e inventario
-- -----------------------------------------------------
CREATE TABLE Producto (
    id_producto  INT AUTO_INCREMENT PRIMARY KEY,
    codigo       VARCHAR(20) NOT NULL UNIQUE,
    nombre       VARCHAR(100) NOT NULL UNIQUE,
    descripcion  VARCHAR(200),
    id_categoria INT NOT NULL,
    id_especie   INT NULL,                      -- NULL = sirve para todas las especies
    id_unidad    INT NOT NULL,

    FOREIGN KEY (id_categoria)
        REFERENCES Categoria(id_categoria),

    FOREIGN KEY (id_especie)
        REFERENCES Especie(id_especie),

    FOREIGN KEY (id_unidad)
        REFERENCES Unidad_Medida(id_unidad)
);

-- Existencia total de cada producto y su stock minimo (un registro por producto)
CREATE TABLE Inventario (
    id_inventario INT AUTO_INCREMENT PRIMARY KEY,
    codigo        VARCHAR(20) NOT NULL UNIQUE,
    id_producto   INT NOT NULL UNIQUE,
    stock_actual  DECIMAL(10,2) NOT NULL DEFAULT 0,
    stock_minimo  DECIMAL(10,2) NOT NULL DEFAULT 0,

    FOREIGN KEY (id_producto)
        REFERENCES Producto(id_producto),

    CHECK (stock_actual >= 0),
    CHECK (stock_minimo >= 0)
);

-- -----------------------------------------------------
-- Donantes y donaciones recibidas
-- -----------------------------------------------------
CREATE TABLE Institucion (
    id_institucion INT AUTO_INCREMENT PRIMARY KEY,
    codigo         VARCHAR(20) NOT NULL UNIQUE,
    nombre         VARCHAR(120) NOT NULL UNIQUE,
    tipo           VARCHAR(50),
    telefono       VARCHAR(20)
);

CREATE TABLE Donante (
    id_donante     INT AUTO_INCREMENT PRIMARY KEY,
    codigo         VARCHAR(20) NOT NULL UNIQUE,
    nombre         VARCHAR(120) NOT NULL,
    tipo_donante   ENUM('PERSONA','INSTITUCION') NOT NULL,
    telefono       VARCHAR(20),
    id_institucion INT NULL,

    FOREIGN KEY (id_institucion)
        REFERENCES Institucion(id_institucion)
);

CREATE TABLE Donacion (
    id_donacion     INT AUTO_INCREMENT PRIMARY KEY,
    codigo          VARCHAR(20) NOT NULL UNIQUE,
    id_donante      INT NOT NULL,
    fecha_recepcion DATE NOT NULL,
    destino         VARCHAR(150) NOT NULL,

    FOREIGN KEY (id_donante)
        REFERENCES Donante(id_donante),

    INDEX idx_donacion_fecha (fecha_recepcion)
);

-- -----------------------------------------------------
-- Inventario por lotes (ya no se enlaza con Donacion)
-- -----------------------------------------------------
CREATE TABLE Lote (
    id_lote           INT AUTO_INCREMENT PRIMARY KEY,
    codigo            VARCHAR(20) NOT NULL UNIQUE,
    id_producto       INT NOT NULL,
    cantidad_inicial  DECIMAL(10,2) NOT NULL,
    cantidad_actual   DECIMAL(10,2) NOT NULL,
    fecha_ingreso     DATE NOT NULL,
    fecha_vencimiento DATE,

    FOREIGN KEY (id_producto)
        REFERENCES Producto(id_producto),

    CHECK (cantidad_inicial > 0),
    CHECK (cantidad_actual >= 0),
    CHECK (cantidad_actual <= cantidad_inicial),

    -- Para elegir el lote que vence primero y listar proximos a vencer
    INDEX idx_lote_producto_vencimiento (id_producto, fecha_vencimiento)
);

-- -----------------------------------------------------
-- Movimientos de stock (entradas y salidas, incluidas las entregas)
-- -----------------------------------------------------
CREATE TABLE Movimiento (
    id_movimiento   INT AUTO_INCREMENT PRIMARY KEY,
    codigo          VARCHAR(20) NOT NULL UNIQUE,
    tipo_movimiento ENUM('ENTRADA','SALIDA') NOT NULL,
    fecha           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_usuario      INT NOT NULL,               -- quien registro el movimiento
    observacion     VARCHAR(200),

    FOREIGN KEY (id_usuario)
        REFERENCES Usuario(id_usuario),

    INDEX idx_movimiento_fecha (fecha)
);

CREATE TABLE Detalle_Movimiento (
    id_detalle    INT AUTO_INCREMENT PRIMARY KEY,
    codigo        VARCHAR(20) NOT NULL UNIQUE,
    id_movimiento INT NOT NULL,
    id_lote       INT NOT NULL,                 -- el producto se obtiene a traves del lote
    cantidad      DECIMAL(10,2) NOT NULL,
    concepto      VARCHAR(150) NOT NULL,        -- entradas y salidas (compra, donacion, alimentacion...)
    destinatario  VARCHAR(100) NULL,            -- solo en salidas

    FOREIGN KEY (id_movimiento)
        REFERENCES Movimiento(id_movimiento),

    FOREIGN KEY (id_lote)
        REFERENCES Lote(id_lote),

    CHECK (cantidad > 0)
);

-- -----------------------------------------------------
-- Mascotas del albergue y cuidados especiales
-- -----------------------------------------------------
CREATE TABLE Mascota (
    id_mascota       INT AUTO_INCREMENT PRIMARY KEY,
    codigo           VARCHAR(20) NOT NULL UNIQUE,
    nombre           VARCHAR(100) NOT NULL,
    id_especie       INT NOT NULL,
    id_raza          INT NULL,
    sexo             ENUM('Macho','Hembra') NOT NULL,
    fecha_nacimiento DATE NULL,                 -- aproximada; la edad se calcula en V_Mascota
    fecha_ingreso    DATE NOT NULL,
    fecha_salida     DATE NULL,

    FOREIGN KEY (id_especie)
        REFERENCES Especie(id_especie),

    FOREIGN KEY (id_raza)
        REFERENCES Raza(id_raza),

    CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso)
);

-- Antes se llamaba Programa
CREATE TABLE Cuidados_Especiales (
    id_cuidado   INT AUTO_INCREMENT PRIMARY KEY,
    codigo       VARCHAR(20) NOT NULL UNIQUE,
    nombre       VARCHAR(120) NOT NULL UNIQUE,
    objetivos    TEXT,
    fecha_inicio DATE,
    fecha_fin    DATE,

    CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio)
);

-- Antes se llamaba Programa_Beneficiario (mascotas inscritas en un cuidado especial)
CREATE TABLE Mascota_Cuidado (
    id_mascota_cuidado INT AUTO_INCREMENT PRIMARY KEY,
    codigo             VARCHAR(20) NOT NULL UNIQUE,
    id_cuidado         INT NOT NULL,
    id_mascota         INT NOT NULL,
    fecha_registro     DATE NOT NULL,

    FOREIGN KEY (id_cuidado)
        REFERENCES Cuidados_Especiales(id_cuidado),

    FOREIGN KEY (id_mascota)
        REFERENCES Mascota(id_mascota),

    UNIQUE (id_cuidado, id_mascota)
);

-- -----------------------------------------------------
-- Beneficiario: lo que recibe cada mascota (consumo por categoria)
-- -----------------------------------------------------
CREATE TABLE Beneficiario (
    cod_beneficiario VARCHAR(20) PRIMARY KEY,
    id_mascota       INT NOT NULL,
    id_categoria     INT NOT NULL,
    fecha            DATE NOT NULL,
    id_unidad        INT NOT NULL,
    cantidad         DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (id_mascota)
        REFERENCES Mascota(id_mascota),

    FOREIGN KEY (id_categoria)
        REFERENCES Categoria(id_categoria),

    FOREIGN KEY (id_unidad)
        REFERENCES Unidad_Medida(id_unidad),

    CHECK (cantidad > 0),

    INDEX idx_beneficiario_fecha (fecha)
);

-- -----------------------------------------------------
-- Vista: mascota con su edad calculada
-- -----------------------------------------------------
CREATE OR REPLACE VIEW V_Mascota AS
SELECT m.*,
       TIMESTAMPDIFF(YEAR, m.fecha_nacimiento, CURDATE()) AS edad
FROM Mascota m;
