from database.connection import db


class ProductoModel:

    @staticmethod
    def listar(solo_activos=True):
        where = "WHERE p.activo=1" if solo_activos else ""
        return db.execute(f"""
            SELECT p.*, c.nombre AS categoria
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            {where}
            ORDER BY p.descripcion
        """)

    @staticmethod
    def buscar(termino):
        like = f"%{termino}%"
        return db.execute("""
            SELECT p.*, c.nombre AS categoria
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.activo=1 AND (p.codigo LIKE %s OR p.descripcion LIKE %s)
            ORDER BY p.descripcion
            LIMIT 20
        """, (like, like))

    @staticmethod
    def por_codigo(codigo):
        return db.fetchone(
            "SELECT * FROM productos WHERE codigo=%s AND activo=1",
            (codigo,)
        )

    @staticmethod
    def obtener(prod_id):
        return db.fetchone("SELECT * FROM productos WHERE id=%s", (prod_id,))

    @staticmethod
    def crear(codigo, descripcion, categoria_id, precio_compra, precio_venta,
              precio_mayorista, stock, stock_minimo, tiene_iva):
        return db.execute(
            """INSERT INTO productos
               (codigo, descripcion, categoria_id, precio_compra, precio_venta,
                precio_mayorista, stock, stock_minimo, tiene_iva)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (codigo, descripcion, categoria_id, precio_compra, precio_venta,
             precio_mayorista, stock, stock_minimo, tiene_iva),
            fetch=False
        )

    @staticmethod
    def actualizar(prod_id, codigo, descripcion, categoria_id, precio_compra,
                   precio_venta, precio_mayorista, stock, stock_minimo, tiene_iva):
        return db.execute(
            """UPDATE productos SET codigo=%s, descripcion=%s, categoria_id=%s,
               precio_compra=%s, precio_venta=%s, precio_mayorista=%s,
               stock=%s, stock_minimo=%s, tiene_iva=%s
               WHERE id=%s""",
            (codigo, descripcion, categoria_id, precio_compra, precio_venta,
             precio_mayorista, stock, stock_minimo, tiene_iva, prod_id),
            fetch=False
        )

    @staticmethod
    def actualizar_stock(prod_id, cantidad):
        return db.execute(
            "UPDATE productos SET stock = stock - %s WHERE id=%s",
            (cantidad, prod_id), fetch=False
        )

    @staticmethod
    def eliminar(prod_id):
        return db.execute(
            "UPDATE productos SET activo=0 WHERE id=%s",
            (prod_id,), fetch=False
        )

    @staticmethod
    def stock_bajo():
        return db.execute("""
            SELECT * FROM productos
            WHERE activo=1 AND stock <= stock_minimo
            ORDER BY stock ASC
        """)

    @staticmethod
    def listar_categorias():
        return db.execute("SELECT * FROM categorias ORDER BY nombre")
