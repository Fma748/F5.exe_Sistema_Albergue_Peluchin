import os
import re
from conexion import conectar
from lector_sql import leer_sentencias

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "Base_de_Datos", "albergue_peluchin_inicial_corregida.sql")

# Tablas de la estructura anterior. Si existen, la base debe recrearse.
TABLAS_ANTERIORES = {"entrega", "programa", "programa_beneficiario"}

sentencias = leer_sentencias(RUTA)

cn = conectar()
if cn is None:
    raise SystemExit("No se pudo conectar. Revisa conexion.py y que MySQL de XAMPP esté en verde.")
cur = cn.cursor()

cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
existentes = {t[0].lower() for t in cur.fetchall()}
if existentes & TABLAS_ANTERIORES:
    cur.close()
    cn.close()
    raise SystemExit(
        "Tu base tiene la estructura ANTERIOR (tablas Entrega / Programa).\n"
        "Para pasar a la estructura nueva ejecuta:  py crear_base.py\n"
        "(borra la base y la crea de nuevo; los datos de prueba se pierden)."
    )

for s in sentencias:
    s = re.sub(r"CREATE TABLE\s+", "CREATE TABLE IF NOT EXISTS ", s, flags=re.I)
    cur.execute(s)
cn.commit()

cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
tablas = [t[0] for t in cur.fetchall()]
print("Nota: si la base ya existía, las reglas nuevas (CHECK) no se agregan a las tablas")
print("      existentes. Para eso ejecuta:  py aplicar_restricciones.py")
print("Tablas en la base:", len(tablas), "(deben ser 17)")
for t in sorted(tablas):
    print(" -", t)
cur.close()
cn.close()
