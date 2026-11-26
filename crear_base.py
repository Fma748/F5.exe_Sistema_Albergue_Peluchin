import os
from getpass import getpass
import mysql.connector
from mysql.connector import Error

from lector_sql import leer_sentencias

RUTA_SQL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "Base_de_Datos", "albergue_peluchin_inicial_corregida.sql")


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

        cur.execute("SHOW FULL TABLES WHERE Table_type = 'BASE TABLE'")
        print("Tablas creadas:", len(cur.fetchall()), "(deben ser 17)")

        cur.execute("SHOW TRIGGERS")
        print("Triggers de validación:", len(cur.fetchall()))
        print("\nSiguiente paso: ejecuta  py crear_admin.py  y luego  py app.py")
    except FileNotFoundError:
        print("No encuentro el archivo SQL. Debe estar en la carpeta Base_de_Datos.")
    except Error as e:
        print("Error al ejecutar el SQL:", e)
    finally:
        cur.close()
        cn.close()


main()
