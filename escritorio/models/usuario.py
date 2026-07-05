import hashlib
from database.connection import db


class UsuarioModel:

    @staticmethod
    def autenticar(usuario, password):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        return db.fetchone(
            "SELECT * FROM usuarios WHERE usuario=%s AND password=%s AND activo=1",
            (usuario, pw_hash)
        )

    @staticmethod
    def listar():
        return db.execute("SELECT id, nombre, usuario, rol, activo FROM usuarios ORDER BY nombre")

    @staticmethod
    def obtener(user_id):
        return db.fetchone("SELECT * FROM usuarios WHERE id=%s", (user_id,))

    @staticmethod
    def crear(nombre, usuario, password, rol='cajero'):
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        return db.execute(
            "INSERT INTO usuarios (nombre, usuario, password, rol) VALUES (%s,%s,%s,%s)",
            (nombre, usuario, pw_hash, rol), fetch=False
        )

    @staticmethod
    def actualizar(user_id, nombre, usuario, rol, activo):
        return db.execute(
            "UPDATE usuarios SET nombre=%s, usuario=%s, rol=%s, activo=%s WHERE id=%s",
            (nombre, usuario, rol, activo, user_id), fetch=False
        )

    @staticmethod
    def cambiar_password(user_id, nueva_password):
        pw_hash = hashlib.sha256(nueva_password.encode()).hexdigest()
        return db.execute(
            "UPDATE usuarios SET password=%s WHERE id=%s",
            (pw_hash, user_id), fetch=False
        )

    @staticmethod
    def eliminar(user_id):
        return db.execute(
            "UPDATE usuarios SET activo=0 WHERE id=%s",
            (user_id,), fetch=False
        )
