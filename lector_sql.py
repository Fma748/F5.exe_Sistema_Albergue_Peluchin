"""Lee un archivo .sql y lo separa en sentencias.

Entiende la instrucción DELIMITER (la misma que usa phpMyAdmin), que hace falta
para los triggers: su cuerpo tiene varios ';' y no se puede cortar en cada uno.
"""
import re


def leer_sentencias(ruta):
    with open(ruta, encoding="utf-8") as f:
        texto = f.read()
    # quita todos los comentarios "-- ..." (incluso los que traen un ';')
    texto = re.sub(r"--[^\n]*", "", texto)

    sentencias, actual, delim = [], [], ";"
    for linea in texto.splitlines():
        limpia = linea.strip()
        if limpia.upper().startswith("DELIMITER"):
            delim = limpia.split()[1]
            continue
        actual.append(linea)
        if limpia.endswith(delim):
            sql = "\n".join(actual).strip()
            sql = sql[: -len(delim)].strip()
            if sql:
                sentencias.append(sql)
            actual = []
    resto = "\n".join(actual).strip()
    if resto:
        sentencias.append(resto)
    return sentencias
