import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Escribe aquí tu contraseña de MySQL
            database="Albergue_Peluchin",
            port=3306
        )
    except Error as e:
        print("Error de conexión:", e)
        return None
