import hashlib
import secrets
import hmac
from conexion import conectar

ITERACIONES = 300000

def generar_hash(contrasena):
    salt = secrets.token_hex(16)
    clave = hashlib.pbkdf2_hmac(
        "sha256", contrasena.encode("utf-8"),
        salt.encode("utf-8"), ITERACIONES
    ).hex()
    return f"pbkdf2_sha256${ITERACIONES}${salt}${clave}"

def verificar_hash(contrasena, hash_guardado):
    try:
        algoritmo, iteraciones, salt, original = hash_guardado.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        clave = hashlib.pbkdf2_hmac(
            "sha256", contrasena.encode("utf-8"),
            salt.encode("utf-8"), int(iteraciones)
        ).hex()
        return hmac.compare_digest(clave, original)
    except (ValueError, TypeError, AttributeError):
        return False

def autenticar(usuario, contrasena):
    cn = conectar()
    if cn is None:
        return None
    cur = cn.cursor()
    try:
        cur.execute("""
            SELECT id_usuario, nombre_usuario, contrasena_hash,
                   nombre_completo, rol, activo
            FROM Usuario WHERE nombre_usuario=%s
        """, (usuario,))
        fila = cur.fetchone()
        if not fila:
            return None
        uid, uname, pwd_hash, nombre, rol, activo = fila
        if activo and verificar_hash(contrasena, pwd_hash):
            return {"id": uid, "usuario": uname, "nombre": nombre, "rol": rol}
        return None
    finally:
        cur.close()
        cn.close()
