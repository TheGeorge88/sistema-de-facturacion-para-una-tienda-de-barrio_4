from database.connection import db


class ClienteModel:

    @staticmethod
    def listar():
        return db.execute(
            "SELECT * FROM clientes WHERE activo=1 ORDER BY nombre, apellido"
        )

    @staticmethod
    def buscar(termino):
        like = f"%{termino}%"
        return db.execute(
            """SELECT * FROM clientes WHERE activo=1
               AND (cedula LIKE %s OR nombre LIKE %s OR apellido LIKE %s)
               ORDER BY nombre LIMIT 20""",
            (like, like, like)
        )

    @staticmethod
    def por_cedula(cedula):
        return db.fetchone(
            "SELECT * FROM clientes WHERE cedula=%s AND activo=1",
            (cedula,)
        )

    @staticmethod
    def obtener(cliente_id):
        return db.fetchone("SELECT * FROM clientes WHERE id=%s", (cliente_id,))

    @staticmethod
    def crear(cedula, nombre, apellido, direccion, telefono, email, tipo):
        return db.execute(
            """INSERT INTO clientes
               (cedula, nombre, apellido, direccion, telefono, email, tipo)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (cedula, nombre, apellido, direccion, telefono, email, tipo),
            fetch=False
        )

    @staticmethod
    def actualizar(cliente_id, cedula, nombre, apellido, direccion, telefono, email, tipo):
        return db.execute(
            """UPDATE clientes SET cedula=%s, nombre=%s, apellido=%s,
               direccion=%s, telefono=%s, email=%s, tipo=%s WHERE id=%s""",
            (cedula, nombre, apellido, direccion, telefono, email, tipo, cliente_id),
            fetch=False
        )

    @staticmethod
    def eliminar(cliente_id):
        return db.execute(
            "UPDATE clientes SET activo=0 WHERE id=%s",
            (cliente_id,), fetch=False
        )

    @staticmethod
    def consumidor_final():
        return db.fetchone(
            "SELECT * FROM clientes WHERE cedula='9999999999'"
        )
