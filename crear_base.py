import os
import re
from getpass import getpass
import mysql.connector
from mysql.connector import Error

RUTA_SQL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "albergue_peluchin_inicial_corregida.sql")

EXTRAS = [
    ("Regla: vencimiento >= ingreso en Lote",
     "ALTER TABLE Lote ADD CONSTRAINT chk_lote_vencimiento "
     "CHECK (fecha_vencimiento IS NULL OR fecha_vencimiento >= fecha_ingreso)"),
    ("Trigger: Entrega solo con movimiento SALIDA",
     """CREATE TRIGGER trg_entrega_solo_salida
        BEFORE INSERT ON Entrega
        FOR EACH ROW
        BEGIN
          IF (SELECT tipo_movimiento FROM Movimiento
              WHERE id_movimiento = NEW.id_movimiento) <> 'SALIDA' THEN
            SIGNAL SQLSTATE '45000'
              SET MESSAGE_TEXT = 'La entrega debe respaldarse con un movimiento de tipo SALIDA';
          END IF;
        END"""),
]


def leer_sentencias(ruta):
    with open(ruta, encoding="utf-8") as f:
        texto = f.read()
    # quita todos los comentarios "-- ..." (incluso los que traen un ';')
    texto = re.sub(r"--[^\n]*", "", texto)
    return [s.strip() for s in texto.split(";") if s.strip()]


def main():
    print("=== CREAR BASE DE DATOS ALBERGUE PELUCHIN ===")
    usuario = input("Usuario de MySQL [root]: ").strip() or "root"
    clave = getpass("Contraseña de MySQL (Enter si no tiene): ")
    try:
        cn = mysql.connector.connect(host="localhost", port=3306, user=usuario, password=clave)
    except Error as e:
        print("No se pudo conectar a MySQL:", e)
        return
    cur = cn.cursor()
    try:
        cur.execute("SHOW DATABASES LIKE 'Albergue_Peluchin'")
        if cur.fetchone():
            r = input("La base Albergue_Peluchin ya existe. ¿Borrarla y crearla de nuevo? "
                      "Se pierden sus datos (s/n): ").strip().lower()
            if r != "s":
                print("Cancelado. No se hizo ningún cambio.")
                return
            cur.execute("DROP DATABASE Albergue_Peluchin")
            cn.commit()
            print("Base anterior borrada.")

        sentencias = leer_sentencias(RUTA_SQL)
        for sql in sentencias:
            cur.execute(sql)
        cn.commit()
        print(f"Base creada correctamente ({len(sentencias)} sentencias ejecutadas).")

        cur.execute("SHOW TABLES")
        print("Tablas creadas:", len(cur.fetchall()), "(deben ser 14)")

        if input("¿Aplicar las mejoras opcionales (regla y trigger)? (s/n): ").strip().lower() == "s":
            for nombre, sql in EXTRAS:
                try:
                    cur.execute(sql)
                    cn.commit()
                    print("OK:", nombre)
                except Error as e:
                    print("No se aplicó:", nombre, "->", e)
    except FileNotFoundError:
        print("No encuentro el archivo SQL. Debe estar en la misma carpeta que crear_base.py.")
    except Error as e:
        print("Error al ejecutar el SQL:", e)
    finally:
        cur.close()
        cn.close()


main()