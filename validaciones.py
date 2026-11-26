"""Reglas de validación del sistema (las mismas que tiene la base de datos).

Las usa app.py (formularios) y aplicar_restricciones.py (mensajes).
"""
import re
from datetime import date
from decimal import Decimal, InvalidOperation

LETRAS = "a-zA-ZáéíóúÁÉÍÓÚñÑüÜ"
TELEFONO_MIN, TELEFONO_MAX = 7, 8
USUARIO_MIN, USUARIO_MAX = 3, 50
NOMBRE_MIN = 2
CANTIDAD_ENTEROS, CANTIDAD_DECIMALES = 6, 2          # hasta 999999.99
CANTIDAD_MAX = Decimal("999999.99")
FECHA_MIN, FECHA_MAX = date(1990, 1, 1), date(2099, 12, 31)


# ----------------------------------------------------------------------
# Comprobaciones (al presionar «Guardar»)
# ----------------------------------------------------------------------
def tiene_letra(texto):
    """Al menos una letra: evita nombres como '12322' o '148548'."""
    return re.search(f"[{LETRAS}]", texto or "") is not None


def es_solo_letras(texto):
    """Letras, espacios, punto, apóstrofo y guion (ej. 'Max', 'Pastor Alemán', 'Ana María')."""
    return re.fullmatch(f"[{LETRAS} .'-]+", texto or "") is not None and tiene_letra(texto)


def es_usuario(texto):
    return re.fullmatch(r"[A-Za-z0-9._]{%d,%d}" % (USUARIO_MIN, USUARIO_MAX), texto or "") is not None


def es_telefono(texto):
    return (texto or "").isdigit() and TELEFONO_MIN <= len(texto) <= TELEFONO_MAX


def leer_cantidad(texto, nombre="La cantidad", permitir_cero=False):
    try:
        c = Decimal((texto or "").strip().replace(",", "."))
    except InvalidOperation:
        raise ValueError(f"{nombre} no es un número válido.")
    if not c.is_finite():
        raise ValueError(f"{nombre} no es un número válido.")
    if c < 0 or (c == 0 and not permitir_cero):
        raise ValueError(f"{nombre} debe ser mayor que cero." if not permitir_cero
                         else f"{nombre} no puede ser negativa.")
    if c > CANTIDAD_MAX:
        raise ValueError(f"{nombre} no puede ser mayor que {CANTIDAD_MAX}.")
    if c != c.quantize(Decimal("0.01")):
        raise ValueError(f"{nombre}: usa como máximo {CANTIDAD_DECIMALES} decimales.")
    return c


def revisar_rango_fecha(f, nombre):
    if not FECHA_MIN <= f <= FECHA_MAX:
        raise ValueError(f"{nombre}: debe estar entre {FECHA_MIN.year} y {FECHA_MAX.year}.")
    return f


# ----------------------------------------------------------------------
# Filtros (mientras se escribe): devuelven el texto corregido.
# Se aplican sobre la variable del campo, así funcionan al escribir,
# al pegar y al cargar un registro, en cualquier versión de Tk.
# ----------------------------------------------------------------------
def filtro_texto(maximo):
    return lambda t: t[:maximo]


def filtro_letras(maximo):
    return lambda t: re.sub(f"[^{LETRAS} .'-]", "", t)[:maximo]


def filtro_digitos(maximo):
    return lambda t: re.sub(r"\D", "", t)[:maximo]


def filtro_usuario(maximo=USUARIO_MAX):
    return lambda t: re.sub(r"[^A-Za-z0-9._]", "", t)[:maximo]


def filtro_fecha(t):
    return re.sub(r"[^0-9-]", "", t)[:10]


def filtro_decimal(t):
    t = re.sub(r"[^0-9.,]", "", t)
    m = re.match(r"(\d*)([.,]?)(\d*)", t)
    enteros, sep, dec = m.group(1), m.group(2), re.sub(r"\D", "", t[m.end(1) + len(m.group(2)):])
    return enteros[:CANTIDAD_ENTEROS] + sep + (dec[:CANTIDAD_DECIMALES] if sep else "")


# ----------------------------------------------------------------------
# Mensajes de las reglas CHECK de la base (mismo nombre que en el archivo .sql)
# ----------------------------------------------------------------------
MENSAJES_REGLAS = {
    "chk_usuario_nombre_usuario": "El nombre de usuario debe tener de 3 a 50 caracteres: letras, números, punto o guion bajo, sin espacios.",
    "chk_usuario_nombre_completo": "El nombre completo solo puede tener letras (mínimo 2).",
    "chk_categoria_nombre": "El nombre de la categoría debe tener letras (no solo números).",
    "chk_unidad_nombre": "El nombre de la unidad debe tener letras (no solo números).",
    "chk_unidad_abreviatura": "La abreviatura debe tener al menos una letra.",
    "chk_especie_nombre": "El nombre de la especie solo puede tener letras (mínimo 2).",
    "chk_raza_nombre": "El nombre de la raza solo puede tener letras (mínimo 2).",
    "chk_producto_nombre": "El nombre del producto debe tener letras (no solo números).",
    "chk_institucion_nombre": "El nombre de la institución debe tener letras (no solo números).",
    "chk_institucion_tipo": "El tipo de institución debe tener letras (no solo números).",
    "chk_institucion_telefono": "El teléfono debe tener 7 u 8 dígitos, solo números.",
    "chk_donante_nombre": "El nombre del donante debe tener letras (no solo números).",
    "chk_donante_telefono": "El teléfono debe tener 7 u 8 dígitos, solo números.",
    "chk_donante_tipo": "Un donante INSTITUCION debe tener institución; una PERSONA no lleva institución.",
    "chk_donacion_destino": "El destino de la donación debe tener letras (no solo números).",
    "chk_donacion_fecha": "La fecha de recepción debe estar entre 1990 y 2099.",
    "chk_lote_vencimiento": "La fecha de vencimiento no puede ser anterior a la de ingreso.",
    "chk_lote_fechas": "Las fechas del lote deben estar entre 1990 y 2099.",
    "chk_detalle_concepto": "El concepto debe tener letras (no solo números).",
    "chk_detalle_destinatario": "El destinatario debe tener letras (no solo números).",
    "chk_mascota_nombre": "El nombre de la mascota solo puede tener letras (mínimo 2).",
    "chk_mascota_nacimiento_ingreso": "La fecha de nacimiento no puede ser posterior a la de ingreso.",
    "chk_mascota_nacimiento_salida": "La fecha de salida no puede ser anterior a la de nacimiento.",
    "chk_mascota_fechas": "Las fechas de la mascota deben estar entre 1990 y 2099.",
    "chk_cuidado_nombre": "El nombre del cuidado especial debe tener letras (no solo números).",
    "chk_cuidado_fechas": "Las fechas del cuidado especial deben estar entre 1990 y 2099.",
    "chk_mascota_cuidado_fecha": "La fecha de inscripción debe estar entre 1990 y 2099.",
    "chk_beneficiario_fecha": "La fecha del consumo debe estar entre 1990 y 2099.",
}
