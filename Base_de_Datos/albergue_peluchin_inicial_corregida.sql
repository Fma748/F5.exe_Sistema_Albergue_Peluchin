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
-- Cambios 26/11/2026 (validaciones):
--   * Nombres: no pueden ser solo numeros (minimo 2 caracteres y una letra)
--   * Nombres de mascota, especie, raza y nombre completo de usuario: solo letras
--   * Nombre de usuario: 3 a 50 caracteres, letras, numeros, punto o guion bajo
--   * Telefonos: solo digitos, de 7 a 8 (VARCHAR(8))
--   * Donante: INSTITUCION lleva institucion; PERSONA no
--   * Todas las fechas entre 1990 y 2099
--   * Mascota: nacimiento <= ingreso <= salida; la raza debe ser de su especie
--   * Fechas que no pueden ser futuras: nacimiento, ingreso de mascota y de lote,
--     recepcion de donacion, consumo e inscripcion (triggers: un CHECK no admite CURDATE())
--   * Consumo e inscripcion: dentro de la estadia de la mascota en el albergue
--   * No se puede ingresar un lote ya vencido
--   * Las reglas de vencimiento del lote y del destinatario ya no son opcionales
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
    activo          BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_usuario_nombre_usuario
        CHECK (nombre_usuario REGEXP '^[A-Za-z0-9._]{3,50}$'),
    CONSTRAINT chk_usuario_nombre_completo
        CHECK (nombre_completo REGEXP '^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ .''-]+$' AND nombre_completo REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(nombre_completo)) >= 2)
);

-- -----------------------------------------------------
-- Listas de apoyo (alimentan los menus desplegables)
-- -----------------------------------------------------
CREATE TABLE Categoria (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    codigo       VARCHAR(20) NOT NULL UNIQUE,
    nombre       VARCHAR(100) NOT NULL UNIQUE,
    descripcion  VARCHAR(200),

    CONSTRAINT chk_categoria_nombre
        CHECK (nombre REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(nombre)) >= 2)
);

CREATE TABLE Unidad_Medida (
    id_unidad   INT AUTO_INCREMENT PRIMARY KEY,
    codigo      VARCHAR(20) NOT NULL UNIQUE,
    nombre      VARCHAR(50) NOT NULL UNIQUE,
    abreviatura VARCHAR(10) NOT NULL UNIQUE,

    CONSTRAINT chk_unidad_nombre
        CHECK (nombre REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(nombre)) >= 2),
    CONSTRAINT chk_unidad_abreviatura
        CHECK (abreviatura REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]')
);

CREATE TABLE Especie (
    id_especie INT AUTO_INCREMENT PRIMARY KEY,
    codigo     VARCHAR(20) NOT NULL UNIQUE,
    nombre     VARCHAR(50) NOT NULL UNIQUE,

    CONSTRAINT chk_especie_nombre
        CHECK (nombre REGEXP '^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ .''-]+$' AND nombre REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(nombre)) >= 2)
);

CREATE TABLE Raza (
    id_raza    INT AUTO_INCREMENT PRIMARY KEY,
    codigo     VARCHAR(20) NOT NULL UNIQUE,
    nombre     VARCHAR(80) NOT NULL,
    id_especie INT NOT NULL,

    FOREIGN KEY (id_especie)
        REFERENCES Especie(id_especie),

    UNIQUE (nombre, id_especie),

    CONSTRAINT chk_raza_nombre
        CHECK (nombre REGEXP '^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ .''-]+$' AND nombre REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(nombre)) >= 2)
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
        REFERENCES Unidad_Medida(id_unidad),

    CONSTRAINT chk_producto_nombre
        CHECK (nombre REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(nombre)) >= 2)
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
    telefono       VARCHAR(8),

    CONSTRAINT chk_institucion_nombre
        CHECK (nombre REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(nombre)) >= 2),
    CONSTRAINT chk_institucion_tipo
        CHECK (tipo IS NULL OR (tipo REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(tipo)) >= 2)),
    CONSTRAINT chk_institucion_telefono
        CHECK (telefono IS NULL OR telefono REGEXP '^[0-9]{7,8}$')
);

CREATE TABLE Donante (
    id_donante     INT AUTO_INCREMENT PRIMARY KEY,
    codigo         VARCHAR(20) NOT NULL UNIQUE,
    nombre         VARCHAR(120) NOT NULL,
    tipo_donante   ENUM('PERSONA','INSTITUCION') NOT NULL,
    telefono       VARCHAR(8),
    id_institucion INT NULL,

    FOREIGN KEY (id_institucion)
        REFERENCES Institucion(id_institucion),

    CONSTRAINT chk_donante_nombre
        CHECK (nombre REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(nombre)) >= 2),
    CONSTRAINT chk_donante_telefono
        CHECK (telefono IS NULL OR telefono REGEXP '^[0-9]{7,8}$'),
    CONSTRAINT chk_donante_tipo
        CHECK ((tipo_donante = 'PERSONA' AND id_institucion IS NULL)
            OR (tipo_donante = 'INSTITUCION' AND id_institucion IS NOT NULL))
);

CREATE TABLE Donacion (
    id_donacion     INT AUTO_INCREMENT PRIMARY KEY,
    codigo          VARCHAR(20) NOT NULL UNIQUE,
    id_donante      INT NOT NULL,
    fecha_recepcion DATE NOT NULL,
    destino         VARCHAR(150) NOT NULL,

    FOREIGN KEY (id_donante)
        REFERENCES Donante(id_donante),

    INDEX idx_donacion_fecha (fecha_recepcion),

    CONSTRAINT chk_donacion_destino
        CHECK (destino REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(destino)) >= 2),
    CONSTRAINT chk_donacion_fecha_rango
        CHECK (fecha_recepcion BETWEEN '1990-01-01' AND '2099-12-31')
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
    CONSTRAINT chk_lote_vencimiento
        CHECK (fecha_vencimiento IS NULL OR fecha_vencimiento >= fecha_ingreso),
    CONSTRAINT chk_lote_ingreso_rango
        CHECK (fecha_ingreso BETWEEN '1990-01-01' AND '2099-12-31'),
    CONSTRAINT chk_lote_vencimiento_rango
        CHECK (fecha_vencimiento IS NULL OR fecha_vencimiento BETWEEN '1990-01-01' AND '2099-12-31'),

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

    CHECK (cantidad > 0),
    CONSTRAINT chk_detalle_concepto
        CHECK (concepto REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(concepto)) >= 2),
    CONSTRAINT chk_detalle_destinatario
        CHECK (destinatario IS NULL OR (destinatario REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(destinatario)) >= 2))
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

    CONSTRAINT chk_mascota_salida_ingreso
        CHECK (fecha_salida IS NULL OR fecha_salida >= fecha_ingreso),
    CONSTRAINT chk_mascota_nombre
        CHECK (nombre REGEXP '^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ .''-]+$' AND nombre REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(nombre)) >= 2),
    CONSTRAINT chk_mascota_nacimiento_ingreso
        CHECK (fecha_nacimiento IS NULL OR fecha_nacimiento <= fecha_ingreso),
    CONSTRAINT chk_mascota_nacimiento_salida
        CHECK (fecha_nacimiento IS NULL OR fecha_salida IS NULL OR fecha_salida >= fecha_nacimiento),
    CONSTRAINT chk_mascota_nacimiento_rango
        CHECK (fecha_nacimiento IS NULL OR fecha_nacimiento BETWEEN '1990-01-01' AND '2099-12-31'),
    CONSTRAINT chk_mascota_ingreso_rango
        CHECK (fecha_ingreso BETWEEN '1990-01-01' AND '2099-12-31'),
    CONSTRAINT chk_mascota_salida_rango
        CHECK (fecha_salida IS NULL OR fecha_salida BETWEEN '1990-01-01' AND '2099-12-31')
);

-- Antes se llamaba Programa
CREATE TABLE Cuidados_Especiales (
    id_cuidado   INT AUTO_INCREMENT PRIMARY KEY,
    codigo       VARCHAR(20) NOT NULL UNIQUE,
    nombre       VARCHAR(120) NOT NULL UNIQUE,
    objetivos    TEXT,
    fecha_inicio DATE,
    fecha_fin    DATE,

    CONSTRAINT chk_cuidado_fin_inicio
        CHECK (fecha_fin IS NULL OR fecha_inicio IS NULL OR fecha_fin >= fecha_inicio),
    CONSTRAINT chk_cuidado_nombre
        CHECK (nombre REGEXP '[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]' AND CHAR_LENGTH(TRIM(nombre)) >= 2),
    CONSTRAINT chk_cuidado_inicio_rango
        CHECK (fecha_inicio IS NULL OR fecha_inicio BETWEEN '1990-01-01' AND '2099-12-31'),
    CONSTRAINT chk_cuidado_fin_rango
        CHECK (fecha_fin IS NULL OR fecha_fin BETWEEN '1990-01-01' AND '2099-12-31')
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

    UNIQUE (id_cuidado, id_mascota),

    CONSTRAINT chk_mascota_cuidado_fecha_rango
        CHECK (fecha_registro BETWEEN '1990-01-01' AND '2099-12-31')
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
    CONSTRAINT chk_beneficiario_fecha_rango
        CHECK (fecha BETWEEN '1990-01-01' AND '2099-12-31'),

    INDEX idx_beneficiario_fecha (fecha)
);

-- -----------------------------------------------------
-- Vista: mascota con su edad calculada
-- -----------------------------------------------------
CREATE OR REPLACE VIEW V_Mascota AS
SELECT m.*,
       TIMESTAMPDIFF(YEAR, m.fecha_nacimiento, CURDATE()) AS edad
FROM Mascota m;

-- =====================================================
-- REGLAS QUE NO PUEDEN SER CHECK
-- Un CHECK no puede usar CURDATE() ni mirar otras tablas,
-- por eso estas reglas se hacen con procedimientos y triggers.
-- =====================================================
DROP TRIGGER IF EXISTS trg_mascota_fechas_ins;
DROP TRIGGER IF EXISTS trg_mascota_fechas_upd;
DROP TRIGGER IF EXISTS trg_mascota_ins;
DROP TRIGGER IF EXISTS trg_mascota_upd;
DROP TRIGGER IF EXISTS trg_raza_upd;
DROP TRIGGER IF EXISTS trg_donacion_ins;
DROP TRIGGER IF EXISTS trg_donacion_upd;
DROP TRIGGER IF EXISTS trg_lote_ins;
DROP TRIGGER IF EXISTS trg_lote_upd;
DROP TRIGGER IF EXISTS trg_detalle_destinatario;
DROP TRIGGER IF EXISTS trg_beneficiario_ins;
DROP TRIGGER IF EXISTS trg_beneficiario_upd;
DROP TRIGGER IF EXISTS trg_mascota_cuidado_ins;
DROP TRIGGER IF EXISTS trg_mascota_cuidado_upd;
DROP PROCEDURE IF EXISTS validar_no_futura;
DROP PROCEDURE IF EXISTS validar_estadia;
DROP PROCEDURE IF EXISTS validar_mascota;

DELIMITER //

-- Error si la fecha es posterior a hoy
CREATE PROCEDURE validar_no_futura(IN p_fecha DATE, IN p_mensaje VARCHAR(128))
BEGIN
    IF p_fecha IS NOT NULL AND p_fecha > CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = p_mensaje;
    END IF;
END//

-- Error si la fecha queda fuera de la estadia de la mascota (entre su ingreso y su salida)
CREATE PROCEDURE validar_estadia(IN p_mascota INT, IN p_fecha DATE, IN p_que VARCHAR(40))
BEGIN
    DECLARE v_ingreso DATE;
    DECLARE v_salida DATE;
    DECLARE v_mensaje VARCHAR(128);
    SELECT fecha_ingreso, fecha_salida INTO v_ingreso, v_salida
      FROM Mascota WHERE id_mascota = p_mascota;
    IF v_ingreso IS NOT NULL AND p_fecha < v_ingreso THEN
        SET v_mensaje = CONCAT(p_que, ' no puede ser anterior al ingreso de la mascota (', v_ingreso, ')');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_mensaje;
    END IF;
    IF v_salida IS NOT NULL AND p_fecha > v_salida THEN
        SET v_mensaje = CONCAT(p_que, ' no puede ser posterior a la salida de la mascota (', v_salida, ')');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_mensaje;
    END IF;
END//

-- Reglas de la mascota: fechas no futuras y raza de su misma especie
CREATE PROCEDURE validar_mascota(IN p_nacimiento DATE, IN p_ingreso DATE,
                                 IN p_especie INT, IN p_raza INT)
BEGIN
    CALL validar_no_futura(p_nacimiento, 'La fecha de nacimiento no puede ser una fecha futura');
    CALL validar_no_futura(p_ingreso, 'La fecha de ingreso no puede ser una fecha futura');
    IF p_raza IS NOT NULL AND NOT EXISTS
       (SELECT 1 FROM Raza r WHERE r.id_raza = p_raza AND r.id_especie = p_especie) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La raza elegida no pertenece a la especie de la mascota';
    END IF;
END//

CREATE TRIGGER trg_mascota_ins BEFORE INSERT ON Mascota
FOR EACH ROW
BEGIN
    CALL validar_mascota(NEW.fecha_nacimiento, NEW.fecha_ingreso, NEW.id_especie, NEW.id_raza);
END//

CREATE TRIGGER trg_mascota_upd BEFORE UPDATE ON Mascota
FOR EACH ROW
BEGIN
    CALL validar_mascota(NEW.fecha_nacimiento, NEW.fecha_ingreso, NEW.id_especie, NEW.id_raza);
    -- los consumos e inscripciones ya registrados deben seguir dentro de la estadia
    IF EXISTS (SELECT 1 FROM Beneficiario b WHERE b.id_mascota = NEW.id_mascota
                 AND (b.fecha < NEW.fecha_ingreso
                      OR (NEW.fecha_salida IS NOT NULL AND b.fecha > NEW.fecha_salida))) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La mascota tiene consumos registrados fuera de esas fechas de ingreso/salida';
    END IF;
    IF EXISTS (SELECT 1 FROM Mascota_Cuidado mc WHERE mc.id_mascota = NEW.id_mascota
                 AND (mc.fecha_registro < NEW.fecha_ingreso
                      OR (NEW.fecha_salida IS NOT NULL AND mc.fecha_registro > NEW.fecha_salida))) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La mascota tiene inscripciones fuera de esas fechas de ingreso/salida';
    END IF;
END//

CREATE TRIGGER trg_raza_upd BEFORE UPDATE ON Raza
FOR EACH ROW
BEGIN
    IF NEW.id_especie <> OLD.id_especie
       AND EXISTS (SELECT 1 FROM Mascota m WHERE m.id_raza = NEW.id_raza) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No se puede cambiar la especie: hay mascotas registradas con esta raza';
    END IF;
END//

CREATE TRIGGER trg_donacion_ins BEFORE INSERT ON Donacion
FOR EACH ROW
BEGIN
    CALL validar_no_futura(NEW.fecha_recepcion, 'La fecha de recepcion no puede ser una fecha futura');
END//

CREATE TRIGGER trg_donacion_upd BEFORE UPDATE ON Donacion
FOR EACH ROW
BEGIN
    CALL validar_no_futura(NEW.fecha_recepcion, 'La fecha de recepcion no puede ser una fecha futura');
END//

CREATE TRIGGER trg_lote_ins BEFORE INSERT ON Lote
FOR EACH ROW
BEGIN
    CALL validar_no_futura(NEW.fecha_ingreso, 'La fecha de ingreso del lote no puede ser una fecha futura');
    IF NEW.fecha_vencimiento IS NOT NULL AND NEW.fecha_vencimiento < CURDATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'No se puede ingresar un producto que ya esta vencido';
    END IF;
END//

CREATE TRIGGER trg_lote_upd BEFORE UPDATE ON Lote
FOR EACH ROW
BEGIN
    IF NEW.fecha_ingreso <> OLD.fecha_ingreso THEN
        CALL validar_no_futura(NEW.fecha_ingreso, 'La fecha de ingreso del lote no puede ser una fecha futura');
    END IF;
END//

-- Destinatario obligatorio en SALIDA y prohibido en ENTRADA (antes era opcional)
CREATE TRIGGER trg_detalle_destinatario BEFORE INSERT ON Detalle_Movimiento
FOR EACH ROW
BEGIN
    DECLARE v_tipo VARCHAR(10);
    SELECT tipo_movimiento INTO v_tipo FROM Movimiento
     WHERE id_movimiento = NEW.id_movimiento;
    IF v_tipo = 'SALIDA' AND (NEW.destinatario IS NULL OR TRIM(NEW.destinatario) = '') THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'En una SALIDA debes indicar el destinatario';
    ELSEIF v_tipo = 'ENTRADA' AND NEW.destinatario IS NOT NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Una ENTRADA no lleva destinatario';
    END IF;
END//

CREATE TRIGGER trg_beneficiario_ins BEFORE INSERT ON Beneficiario
FOR EACH ROW
BEGIN
    CALL validar_no_futura(NEW.fecha, 'La fecha del consumo no puede ser una fecha futura');
    CALL validar_estadia(NEW.id_mascota, NEW.fecha, 'La fecha del consumo');
END//

CREATE TRIGGER trg_beneficiario_upd BEFORE UPDATE ON Beneficiario
FOR EACH ROW
BEGIN
    CALL validar_no_futura(NEW.fecha, 'La fecha del consumo no puede ser una fecha futura');
    CALL validar_estadia(NEW.id_mascota, NEW.fecha, 'La fecha del consumo');
END//

CREATE TRIGGER trg_mascota_cuidado_ins BEFORE INSERT ON Mascota_Cuidado
FOR EACH ROW
BEGIN
    CALL validar_no_futura(NEW.fecha_registro, 'La fecha de inscripcion no puede ser una fecha futura');
    CALL validar_estadia(NEW.id_mascota, NEW.fecha_registro, 'La fecha de inscripcion');
END//

CREATE TRIGGER trg_mascota_cuidado_upd BEFORE UPDATE ON Mascota_Cuidado
FOR EACH ROW
BEGIN
    CALL validar_no_futura(NEW.fecha_registro, 'La fecha de inscripcion no puede ser una fecha futura');
    CALL validar_estadia(NEW.id_mascota, NEW.fecha_registro, 'La fecha de inscripcion');
END//

DELIMITER ;
