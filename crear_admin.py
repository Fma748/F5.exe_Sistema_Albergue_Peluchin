from getpass import getpass
from conexion import conectar
from seguridad import generar_hash

print("=== ALBERGUE DE MASCOTAS PELUCHIN ===")
print("CREAR USUARIO ADMINISTRADOR")
usuario = input("Nombre de usuario: ").strip()
nombre = input("Nombre completo: ").strip()
clave = getpass("Contraseña (mínimo 8 caracteres): ")
confirmar = getpass("Confirmar contraseña: ")

if not usuario or not nombre or not clave:
    print("Todos los campos son obligatorios.")
elif len(clave) < 8:
    print("La contraseña debe tener al menos 8 caracteres.")
elif clave != confirmar:
    print("Las contraseñas no coinciden.")
else:
    cn = conectar()
    if cn:
        cur = cn.cursor()
        try:
            cur.execute("SELECT COALESCE(MAX(CAST(SUBSTRING_INDEX(codigo,'-',-1) AS UNSIGNED)),0)+1 FROM Usuario")
            codigo = f"USR-{int(cur.fetchone()[0]):04d}"
            cur.execute("""
                INSERT INTO Usuario
                (codigo, nombre_usuario, contrasena_hash, nombre_completo, rol, activo)
                VALUES (%s, %s, %s, %s, 'ADMIN', TRUE)
            """, (codigo, usuario, generar_hash(clave), nombre))
            cn.commit()
            print(f"Administrador creado correctamente (código {codigo}).")
        except Exception as e:
            cn.rollback()
            print("No se pudo crear el usuario:", e)
        finally:
            cur.close()
            cn.close()
    else:
        print("No se pudo conectar a MySQL.")
