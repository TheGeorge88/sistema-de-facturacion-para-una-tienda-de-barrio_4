from database.connection import db
from datetime import date


class EgresoCajaModel:

    @staticmethod
    def crear(concepto, monto, metodo_pago, observacion, usuario_id):
        return db.execute(
            """INSERT INTO egresos_caja (fecha, concepto, monto, metodo_pago, observacion, usuario_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (date.today(), concepto, monto, metodo_pago, observacion, usuario_id),
            fetch=False
        )

    @staticmethod
    def listar_dia(fecha=None):
        f = fecha or date.today().strftime('%Y-%m-%d')
        return db.execute(
            """SELECT ec.*, u.nombre AS cajero
               FROM egresos_caja ec
               LEFT JOIN usuarios u ON ec.usuario_id = u.id
               WHERE ec.fecha = %s
               ORDER BY ec.created_at DESC""",
            (f,)
        )

    @staticmethod
    def listar_rango(fecha_ini, fecha_fin):
        return db.execute(
            """SELECT ec.*, u.nombre AS cajero
               FROM egresos_caja ec
               LEFT JOIN usuarios u ON ec.usuario_id = u.id
               WHERE ec.fecha BETWEEN %s AND %s
               ORDER BY ec.fecha DESC, ec.created_at DESC""",
            (fecha_ini, fecha_fin)
        )

    @staticmethod
    def total_dia(fecha=None):
        f = fecha or date.today().strftime('%Y-%m-%d')
        row = db.fetchone(
            "SELECT COALESCE(SUM(monto), 0) AS total FROM egresos_caja WHERE fecha = %s",
            (f,)
        )
        return float(row['total']) if row else 0.0

    @staticmethod
    def eliminar(egreso_id):
        return db.execute(
            "DELETE FROM egresos_caja WHERE id = %s",
            (egreso_id,), fetch=False
        )


class EgresoInventarioModel:

    @staticmethod
    def crear(producto_id, cantidad, motivo, observacion, usuario_id):
        ok = db.execute(
            """INSERT INTO egresos_inventario
               (fecha, producto_id, cantidad, motivo, observacion, usuario_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (date.today(), producto_id, cantidad, motivo, observacion, usuario_id),
            fetch=False
        )
        if ok:
            db.execute(
                "UPDATE productos SET stock = GREATEST(0, stock - %s) WHERE id = %s",
                (cantidad, producto_id), fetch=False
            )
        return ok

    @staticmethod
    def listar_dia(fecha=None):
        f = fecha or date.today().strftime('%Y-%m-%d')
        return db.execute(
            """SELECT ei.*, p.descripcion AS producto, p.codigo,
                      u.nombre AS cajero
               FROM egresos_inventario ei
               JOIN productos p ON ei.producto_id = p.id
               LEFT JOIN usuarios u ON ei.usuario_id = u.id
               WHERE ei.fecha = %s
               ORDER BY ei.created_at DESC""",
            (f,)
        )

    @staticmethod
    def listar_rango(fecha_ini, fecha_fin):
        return db.execute(
            """SELECT ei.*, p.descripcion AS producto, p.codigo,
                      u.nombre AS cajero
               FROM egresos_inventario ei
               JOIN productos p ON ei.producto_id = p.id
               LEFT JOIN usuarios u ON ei.usuario_id = u.id
               WHERE ei.fecha BETWEEN %s AND %s
               ORDER BY ei.fecha DESC, ei.created_at DESC""",
            (fecha_ini, fecha_fin)
        )
