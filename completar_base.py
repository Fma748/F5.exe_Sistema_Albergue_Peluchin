import os
import re
from conexion import conectar

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "albergue_peluchin_inicial_corregida.sql")

with open(RUTA, encoding="utf-8") as f:
    texto = f.read()

texto = re.sub(r"--[^\n]*", "", texto)          # quita comentarios
sentencias = [s.strip() for s in texto.split(";") if s.strip()]

cn = conectar()
if cn is None:
    raise SystemExit("No se pudo conectar. Revisa conexion.py y que MySQL de XAMPP esté en verde.")
cur = cn.cursor()
for s in sentencias:
    s = re.sub(r"CREATE TABLE\s+", "CREATE TABLE IF NOT EXISTS ", s, flags=re.I)
    cur.execute(s)
cn.commit()

cur.execute("SHOW TABLES")
tablas = [t[0] for t in cur.fetchall()]
print("Tablas en la base:", len(tablas), "(deben ser 14)")
for t in sorted(tablas):
    print(" -", t)
cur.close()
cn.close()