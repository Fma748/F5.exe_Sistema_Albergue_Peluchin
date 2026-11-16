-- =====================================================
-- Albergue Peluchin - Inventario y suministros
-- Base de datos inicial, corregida y optimizada (14 tablas)
-- Requiere MySQL 8.0.16 o superior (para que los CHECK se apliquen)
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
    nombre_usuario  VARCHAR(50) NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,      -- guardar el hash, nunca la contrasena en texto plano
    nombre_completo VARCHAR(120) NOT NULL,
    rol             ENUM('ADMIN','OPERADOR') NOT NULL DEFAULT 'OPERADOR',
    activo          BOOLEAN NOT NULL DEFAULT TRUE
);

-- -----------------------------------------------------
-- Catalogo de productos
-- -----------------------------------------------------
CREATE TABLE Categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL UNIQUE,
    descripcion  VARCHAR(200)
);

CREATE TABLE Unidad_Medida (
    id_unidad   INT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(50) NOT NULL UNIQUE,
    abreviatura VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE Producto (
    id_producto  INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL UNIQUE,
    descripcion  VARCHAR(200),
    stock_minimo DECIMAL(10,2) NOT NULL DEFAULT 0,
    id_categoria INT NOT NULL,
    id_unidad    INT NOT NULL,

    FOREIGN KEY (id_categoria)
        REFERENCES Categoria(id_categoria),

    FOREIGN KEY (id_unidad)
        REFERENCES Unidad_Medida(id_unidad),

    CHECK (stock_minimo >= 0)
);

-- -----------------------------------------------------
-- Donantes y donaciones recibidas
-- -----------------------------------------------------
CREATE TABLE Institucion (
    id_institucion INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(120) NOT NULL UNIQUE,
    tipo           VARCHAR(50),
    telefono       VARCHAR(20)
);

CREATE TABLE Donante (
    id_donante     INT AUTO_INCREMENT PRIMARY KEY,
    nombre         VARCHAR(120) NOT NULL,
    tipo_donante   ENUM('PERSONA','INSTITUCION') NOT NULL,
    telefono       VARCHAR(20),
    id_institucion INT NULL,

    FOREIGN KEY (id_institucion)
        REFERENCES Institucion(id_institucion)
);

CREATE TABLE Donacion (
    id_donacion     INT AUTO_INCREMENT PRIMARY KEY,
    codigo          VARCHAR(30) NOT NULL UNIQUE,
    id_donante      INT NOT NULL,
    fecha_recepcion DATE NOT NULL,
    destino         VARCHAR(150) NOT NULL,

    FOREIGN KEY (id_donante)
        REFERENCES Donante(id_donante),

    INDEX idx_donacion_fecha (fecha_recepcion)
);

-- -----------------------------------------------------
-- Inventario por lotes
-- -----------------------------------------------------
CREATE TABLE Lote (
    id_lote           INT AUTO_INCREMENT PRIMARY KEY,
    id_producto       INT NOT NULL,
    id_donacion       INT NULL,                 -- NUEVO: donacion de origen; NULL si fue comprado
    cantidad_inicial  DECIMAL(10,2) NOT NULL,
    cantidad_actual   DECIMAL(10,2) NOT NULL,
    fecha_ingreso     DATE NOT NULL,
    fecha_vencimiento DATE,

    FOREIGN KEY (id_producto)
        REFERENCES Producto(id_producto),

    FOREIGN KEY (id_donacion)
        REFERENCES Donacion(id_donacion),

    CHECK (cantidad_inicial > 0),
    CHECK (cantidad_actual >= 0),
    CHECK (cantidad_actual <= cantidad_inicial),

    -- Para elegir el lote que vence primero y listar proximos a vencer
    INDEX idx_lote_producto_vencimiento (id_producto, fecha_vencimiento)
);

-- -----------------------------------------------------
-- Movimientos de stock (entradas y salidas)
-- -----------------------------------------------------
CREATE TABLE Movimiento (
    id_movimiento   INT AUTO_INCREMENT PRIMARY KEY,
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
    id_movimiento INT NOT NULL,
    id_lote       INT NOT NULL,                 -- el producto se obtiene a traves del lote
    cantidad      DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (id_movimiento)
        REFERENCES Movimiento(id_movimiento),

    FOREIGN KEY (id_lote)
        REFERENCES Lote(id_lote),

    CHECK (cantidad > 0)
);

-- -----------------------------------------------------
-- Programas y beneficiarios (mascotas del albergue)
-- -----------------------------------------------------
CREATE TABLE Programa (
    id_programa  INT AUTO_INCREMENT PRIMARY KEY,
    nombre       VARCHAR(120) NOT NULL UNIQUE,
    objetivos    TEXT,
    fecha_inicio DATE,
    fecha_fin    DATE,

    CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio)
);

CREATE TABLE Beneficiario (
    id_beneficiario INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(100) NOT NULL,
    especie         VARCHAR(50) NOT NULL,
    raza            VARCHAR(100),
    sexo            ENUM('Macho','Hembra') NOT NULL,
    edad_aprox      INT,
    fecha_ingreso   DATE NOT NULL,

    CHECK (edad_aprox >= 0)
);

CREATE TABLE Programa_Beneficiario (
    id_programa     INT NOT NULL,
    id_beneficiario INT NOT NULL,
    fecha_registro  DATE NOT NULL,

    PRIMARY KEY (id_programa, id_beneficiario),

    FOREIGN KEY (id_programa)
        REFERENCES Programa(id_programa),

    FOREIGN KEY (id_beneficiario)
        REFERENCES Beneficiario(id_beneficiario)
);

-- -----------------------------------------------------
-- Entregas a beneficiarios inscritos en un programa
-- Cada entrega es un Movimiento de tipo SALIDA; los productos,
-- lotes y cantidades entregados estan en su Detalle_Movimiento.
-- -----------------------------------------------------
CREATE TABLE Entrega (
    id_entrega      INT AUTO_INCREMENT PRIMARY KEY,
    id_programa     INT NOT NULL,
    id_beneficiario INT NOT NULL,
    id_movimiento   INT NOT NULL UNIQUE,        -- NUEVO: salida de stock que respalda la entrega
    fecha_entrega   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Garantiza que el beneficiario este inscrito en el programa
    FOREIGN KEY (id_programa, id_beneficiario)
        REFERENCES Programa_Beneficiario(id_programa, id_beneficiario),

    FOREIGN KEY (id_movimiento)
        REFERENCES Movimiento(id_movimiento),

    INDEX idx_entrega_fecha (fecha_entrega)
);
