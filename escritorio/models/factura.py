from database.connection import db
import config


class FacturaModel:

    @staticmethod
    def siguiente_numero():
        row = db.fetchone("SELECT MAX(id) AS max_id FROM facturas")
        next_id = (row['max_id'] or 0) + 1
        return f"{config.PREFIJO_FACTURA}{next_id:09d}"

    @staticmethod
    def crear(numero, cliente_id, usuario_id, subtotal, iva, descuento,
              total, forma_pago, tipo_comprobante, items):
        factura_id = db.execute(
            """INSERT INTO facturas
               (numero, cliente_id, usuario_id, subtotal, iva, descuento,
                total, forma_pago, tipo_comprobante)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (numero, cliente_id, usuario_id, subtotal, iva, descuento,
             total, forma_pago, tipo_comprobante),
            fetch=False
        )
        if factura_id:
            for item in items:
                db.execute(
                    """INSERT INTO detalle_facturas
                       (factura_id, producto_id, descripcion, cantidad,
                        precio_unitario, tiene_iva, subtotal)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (factura_id, item['producto_id'], item['descripcion'],
                     item['cantidad'], item['precio_unitario'],
                     item['tiene_iva'], item['subtotal']),
                    fetch=False
                )
            return factura_id
        return None

    @staticmethod
    def obtener(factura_id):
        return db.fetchone("SELECT * FROM facturas WHERE id=%s", (factura_id,))

    @staticmethod
    def obtener_con_detalle(factura_id):
        factura = db.fetchone("""
            SELECT f.*, c.cedula, c.nombre AS cliente_nombre,
                   c.apellido AS cliente_apellido, c.direccion,
                   u.nombre AS cajero
            FROM facturas f
            LEFT JOIN clientes c ON f.cliente_id = c.id
            LEFT JOIN usuarios u ON f.usuario_id = u.id
            WHERE f.id=%s
        """, (factura_id,))
        items = db.execute(
            "SELECT * FROM detalle_facturas WHERE factura_id=%s",
            (factura_id,)
        )
        return factura, items

    @staticmethod
    def anular(factura_id):
        return db.execute(
            "UPDATE facturas SET estado='anulada' WHERE id=%s",
            (factura_id,), fetch=False
        )

    @staticmethod
    def listar_dia(fecha=None):
        if fecha:
            return db.execute("""
                SELECT f.*, c.nombre AS cliente_nombre, c.apellido AS cliente_apellido
                FROM facturas f
                LEFT JOIN clientes c ON f.cliente_id = c.id
                WHERE DATE(f.fecha)=%s AND f.estado='activa'
                ORDER BY f.fecha DESC
            """, (fecha,))
        return db.execute("""
            SELECT f.*, c.nombre AS cliente_nombre, c.apellido AS cliente_apellido
            FROM facturas f
            LEFT JOIN clientes c ON f.cliente_id = c.id
            WHERE DATE(f.fecha)=CURDATE() AND f.estado='activa'
            ORDER BY f.fecha DESC
        """)

    @staticmethod
    def listar_rango(fecha_ini, fecha_fin):
        return db.execute("""
            SELECT f.*, c.nombre AS cliente_nombre, c.apellido AS cliente_apellido
            FROM facturas f
            LEFT JOIN clientes c ON f.cliente_id = c.id
            WHERE DATE(f.fecha) BETWEEN %s AND %s AND f.estado='activa'
            ORDER BY f.fecha DESC
        """, (fecha_ini, fecha_fin))

    @staticmethod
    def resumen_dia(fecha=None):
        if fecha:
            return db.fetchone("""
                SELECT
                    COUNT(*) AS num_facturas,
                    COALESCE(SUM(subtotal),0) AS total_subtotal,
                    COALESCE(SUM(iva),0) AS total_iva,
                    COALESCE(SUM(descuento),0) AS total_descuento,
                    COALESCE(SUM(total),0) AS total_ventas
                FROM facturas
                WHERE DATE(fecha)=%s AND estado='activa'
            """, (fecha,))
        return db.fetchone("""
            SELECT
                COUNT(*) AS num_facturas,
                COALESCE(SUM(subtotal),0) AS total_subtotal,
                COALESCE(SUM(iva),0) AS total_iva,
                COALESCE(SUM(descuento),0) AS total_descuento,
                COALESCE(SUM(total),0) AS total_ventas
            FROM facturas
            WHERE DATE(fecha)=CURDATE() AND estado='activa'
        """)

    @staticmethod
    def productos_mas_vendidos(fecha_ini=None, fecha_fin=None, limit=10):
        if fecha_ini and fecha_fin:
            return db.execute("""
                SELECT df.descripcion, SUM(df.cantidad) AS total_vendido,
                       SUM(df.subtotal) AS total_ventas
                FROM detalle_facturas df
                JOIN facturas f ON df.factura_id = f.id
                WHERE DATE(f.fecha) BETWEEN %s AND %s AND f.estado='activa'
                GROUP BY df.producto_id, df.descripcion
                ORDER BY total_vendido DESC
                LIMIT %s
            """, (fecha_ini, fecha_fin, limit))
        return db.execute("""
            SELECT df.descripcion, SUM(df.cantidad) AS total_vendido,
                   SUM(df.subtotal) AS total_ventas
            FROM detalle_facturas df
            JOIN facturas f ON df.factura_id = f.id
            WHERE f.estado='activa'
            GROUP BY df.producto_id, df.descripcion
            ORDER BY total_vendido DESC
            LIMIT %s
        """, (limit,))

    @staticmethod
    def guardar_cierre(usuario_id, total_efectivo, total_tarjeta,
                       total_otros, total_general, num_facturas, obs=''):
        from datetime import date
        return db.execute(
            """INSERT INTO cierre_caja
               (fecha, usuario_id, total_efectivo, total_tarjeta, total_otros,
                total_general, num_facturas, observaciones)
               VALUES (CURDATE(),%s,%s,%s,%s,%s,%s,%s)""",
            (usuario_id, total_efectivo, total_tarjeta, total_otros,
             total_general, num_facturas, obs),
            fetch=False
        )

    @staticmethod
    def listar_cierres():
        return db.execute("""
            SELECT cc.*, u.nombre AS cajero
            FROM cierre_caja cc
            LEFT JOIN usuarios u ON cc.usuario_id = u.id
            ORDER BY cc.fecha DESC, cc.created_at DESC
            LIMIT 30
        """)
