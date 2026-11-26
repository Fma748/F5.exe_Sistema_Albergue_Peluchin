"""Agrega las validaciones nuevas (26/11/2026) a una base Albergue_Peluchin que YA EXISTE,
sin borrar los datos.

    py aplicar_restricciones.py

1. Lee las reglas (CONSTRAINT ... CHECK), procedimientos y triggers del archivo .sql principal.
2. Busca registros que ya no cumplen las reglas (ej. mascota "111", nacida en 2028,
   teléfono de 18 dígitos) y te deja corregirlos aquí mismo.
3. Cuando no queda ningún registro incorrecto, agrega las reglas y los triggers.
Se puede ejecutar varias veces sin problema.
"""
import os
import re

from conexion import conectar
from lector_sql import leer_sentencias
import validaciones as V

RUTA_SQL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "Base_de_Datos", "albergue_peluchin_inicial_corregida.sql")

# Columna que identifica cada registro (casi todas usan "codigo")
CODIGO = {"Beneficiario": "cod_beneficiario"}

# Columnas que cambian de tamaño
COLUMNAS = [("Institucion", "telefono VARCHAR(8) NULL"),
            ("Donante", "telefono VARCHAR(8) NULL")]

ESTADIA = ("{c} < (SELECT m.fecha_ingreso FROM Mascota m WHERE m.id_mascota = {t}.id_mascota) "
           "OR {c} > (SELECT COALESCE(m.fecha_salida, '9999-12-31') FROM Mascota m "
           "WHERE m.id_mascota = {t}.id_mascota)")

# Reglas que la base controla con triggers (no son CHECK): tabla, campo, condición de error, qué se pide
REGLAS_TRIGGER = [
    ("Mascota", "fecha_nacimiento", "fecha_nacimiento > CURDATE()", "no puede ser futura"),
    ("Mascota", "fecha_ingreso", "fecha_ingreso > CURDATE()", "no puede ser futura"),
    ("Mascota", "id_raza",
     "id_raza IS NOT NULL AND NOT EXISTS (SELECT 1 FROM Raza r WHERE r.id_raza = Mascota.id_raza "
     "AND r.id_especie = Mascota.id_especie)",
     "la raza no es de su especie: Enter para quitarla y elígela luego en el programa"),
    ("Donacion", "fecha_recepcion", "fecha_recepcion > CURDATE()", "no puede ser futura"),
    ("Lote", "fecha_ingreso", "fecha_ingreso > CURDATE()", "no puede ser futura"),
    ("Beneficiario", "fecha", "fecha > CURDATE() OR " + ESTADIA.format(c="fecha", t="Beneficiario"),
     "no futura y dentro de la estadía de la mascota (entre su ingreso y su salida)"),
    ("Mascota_Cuidado", "fecha_registro",
     "fecha_registro > CURDATE() OR " + ESTADIA.format(c="fecha_registro", t="Mascota_Cuidado"),
     "no futura y dentro de la estadía de la mascota (entre su ingreso y su salida)"),
]


def parentesis(texto, inicio):
    """Devuelve lo que hay entre el '(' en la posición inicio y su ')'."""
    nivel = 0
    for i in range(inicio, len(texto)):
        if texto[i] == "(":
            nivel += 1
        elif texto[i] == ")":
            nivel -= 1
            if nivel == 0:
                return texto[inicio + 1:i]
    raise ValueError("Paréntesis sin cerrar en el SQL")


def reglas_del_sql(sentencias):
    reglas = []   # (tabla, nombre, expresion)
    for s in sentencias:
        m = re.match(r"CREATE TABLE\s+(\w+)", s, re.I)
        if not m:
            continue
        for c in re.finditer(r"CONSTRAINT\s+(\w+)\s+CHECK\s*\(", s, re.I):
            reglas.append((m.group(1), c.group(1), parentesis(s, c.end() - 1)))
    return reglas


def columnas(cur, tabla):
    """{columna: acepta_null}"""
    cur.execute("""SELECT COLUMN_NAME, IS_NULLABLE FROM information_schema.COLUMNS
                   WHERE TABLE_SCHEMA = DATABASE() AND LOWER(TABLE_NAME) = LOWER(%s)
                   ORDER BY ORDINAL_POSITION""", (tabla,))
    return {c.lower(): n == "YES" for c, n in cur.fetchall()}


def campo_de_regla(expr, cols):
    """La primera columna que aparece en la regla es la que se pide corregir."""
    for palabra in re.findall(r"[A-Za-z_]\w*", expr):
        if palabra.lower() in cols:
            return palabra.lower()
    return None


def que_pide(nombre_regla):
    if nombre_regla in V.MENSAJES_REGLAS:
        return V.MENSAJES_REGLAS[nombre_regla]
    if nombre_regla.endswith("_rango"):
        return f"AAAA-MM-DD entre {V.FECHA_MIN.year} y {V.FECHA_MAX.year}"
    return "no cumple la regla " + nombre_regla


def buscar_problemas(cur, reglas):
    """Lista de (tabla, codigo, campo, valor_actual, que_se_pide, puede_quedar_vacio)."""
    problemas, vistos = [], set()

    def agregar(tabla, campo, donde, pide):
        cols = columnas(cur, tabla)
        cod = CODIGO.get(tabla, "codigo")
        cur.execute(f"SELECT `{cod}`, `{campo}` FROM `{tabla}` WHERE {donde}")
        for codigo, valor in cur.fetchall():
            if (tabla, codigo, campo) not in vistos:       # una celda puede romper dos reglas
                vistos.add((tabla, codigo, campo))
                problemas.append((tabla, codigo, campo, valor, pide, cols.get(campo, False)))

    for tabla, nombre, expr in reglas:
        campo = campo_de_regla(expr, columnas(cur, tabla))
        agregar(tabla, campo, f"NOT ({expr})", que_pide(nombre))
    for tabla, campo, donde, pide in REGLAS_TRIGGER:
        agregar(tabla, campo, donde, pide)
    return problemas


def arreglos_automaticos(cur):
    """Lo que tiene una sola corrección posible."""
    cur.execute("UPDATE Donante SET id_institucion = NULL "
                "WHERE tipo_donante = 'PERSONA' AND id_institucion IS NOT NULL")
    if cur.rowcount:
        print(f"Corregido: {cur.rowcount} donante(s) PERSONA tenían institución; se les quitó.")


def existe_regla(cur, tabla, nombre):
    cur.execute("""SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
                   WHERE CONSTRAINT_SCHEMA = DATABASE() AND LOWER(TABLE_NAME) = LOWER(%s)
                     AND CONSTRAINT_NAME = %s AND CONSTRAINT_TYPE = 'CHECK'""", (tabla, nombre))
    return cur.fetchone()[0] > 0


def main():
    print("=== APLICAR VALIDACIONES NUEVAS A LA BASE ALBERGUE_PELUCHIN ===")
    sentencias = leer_sentencias(RUTA_SQL)
    reglas = reglas_del_sql(sentencias)
    rutinas = [s for s in sentencias if re.match(r"(DROP|CREATE)\s+(TRIGGER|PROCEDURE)\b", s, re.I)]

    cn = conectar()
    if cn is None:
        raise SystemExit("No se pudo conectar. Revisa conexion.py y que MySQL de XAMPP esté en verde.")
    cur = cn.cursor()
    try:
        arreglos_automaticos(cur)
        cn.commit()

        # 1. Registros que ya no cumplen las reglas
        problemas = buscar_problemas(cur, reglas)
        if problemas:
            print(f"\nHay {len(problemas)} dato(s) que no cumplen las reglas nuevas.")
            print("Escribe el valor correcto de cada uno (Enter = dejarlo vacío si se puede, o saltarlo).\n")
            for tabla, codigo, campo, valor, pide, nulo in problemas:
                print(f"  {codigo}  ({tabla}.{campo})  valor actual: '{valor}'  -> {pide}")
                cod = CODIGO.get(tabla, "codigo")
                while True:
                    nuevo = input("     nuevo valor" + (" [Enter = vacío]" if nulo else " [Enter = saltar]")
                                  + ": ").strip()
                    if not nuevo and not nulo:
                        break
                    try:
                        cur.execute(f"UPDATE `{tabla}` SET `{campo}` = %s WHERE `{cod}` = %s",
                                    (nuevo or None, codigo))
                        if any(p[:3] == (tabla, codigo, campo) for p in buscar_problemas(cur, reglas)):
                            cn.rollback()
                            print("     Ese valor tampoco cumple la regla. Intenta otra vez.")
                            continue
                        cn.commit()
                    except Exception as e:
                        cn.rollback()
                        print("     No se pudo cambiar:", getattr(e, "msg", e))
                        continue
                    break
            problemas = buscar_problemas(cur, reglas)
            if problemas:
                print("\nTodavía quedan datos incorrectos:")
                for tabla, codigo, campo, valor, *_ in problemas:
                    print(f"  - {codigo}  {tabla}.{campo} = '{valor}'")
                print("\nNo se aplicó ninguna regla. Corrígelos (aquí o en el programa) y vuelve a ejecutar.")
                return

        # 2. Tamaño de columnas
        for tabla, definicion in COLUMNAS:
            cur.execute(f"ALTER TABLE `{tabla}` MODIFY {definicion}")
            print(f"OK: {tabla}.{definicion}")

        # 3. Reglas CHECK (si ya existían se reemplazan)
        for tabla, nombre, expr in reglas:
            if existe_regla(cur, tabla, nombre):
                cur.execute(f"ALTER TABLE `{tabla}` DROP CONSTRAINT `{nombre}`")
            cur.execute(f"ALTER TABLE `{tabla}` ADD CONSTRAINT `{nombre}` CHECK ({expr})")
        print(f"OK: {len(reglas)} reglas CHECK")

        # 4. Procedimientos y triggers
        for s in rutinas:
            cur.execute(s)
        creados = sum(1 for s in rutinas if s.upper().startswith("CREATE"))
        print(f"OK: {creados} procedimientos y triggers de validación")
        cn.commit()
        print("\nListo. La base ya tiene todas las validaciones nuevas.")
    except (KeyboardInterrupt, EOFError):
        cn.rollback()
        print("\nCancelado. Las correcciones ya confirmadas se mantienen; las reglas no se aplicaron.")
    except Exception as e:
        cn.rollback()
        print("Error:", getattr(e, "msg", e))
    finally:
        cur.close()
        cn.close()


if __name__ == "__main__":
    main()
