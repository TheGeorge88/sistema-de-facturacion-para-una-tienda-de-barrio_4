import mysql.connector
from mysql.connector import Error
import hashlib
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = None
            cls._instance.cursor = None
        return cls._instance

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**config.DB_CONFIG)
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Error as e:
            print(f"Error conectando a MySQL: {e}")
            return False

    def setup_database(self):
        try:
            conf = {k: v for k, v in config.DB_CONFIG.items() if k != 'database'}
            tmp = mysql.connector.connect(**conf)
            cur = tmp.cursor()
            db_name = config.DB_CONFIG['database']
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cur.execute(f"USE `{db_name}`")
            self._create_tables(cur)
            self._insert_defaults(cur)
            tmp.commit()
            cur.close()
            tmp.close()
            return self.connect()
        except Error as e:
            print(f"Error configurando base de datos: {e}")
            return False

    def _create_tables(self, cur):
        sqls = [
            """CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                usuario VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                rol ENUM('admin','cajero') DEFAULT 'cajero',
                activo TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS categorias (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT
            ) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS productos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                descripcion VARCHAR(255) NOT NULL,
                categoria_id INT DEFAULT NULL,
                precio_compra DECIMAL(10,2) DEFAULT 0.00,
                precio_venta DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                precio_mayorista DECIMAL(10,2) DEFAULT 0.00,
                stock INT DEFAULT 0,
                stock_minimo INT DEFAULT 5,
                tiene_iva TINYINT(1) DEFAULT 1,
                activo TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
            ) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                cedula VARCHAR(20) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) DEFAULT '',
                direccion TEXT,
                telefono VARCHAR(20) DEFAULT '',
                email VARCHAR(100) DEFAULT '',
                tipo ENUM('natural','juridico') DEFAULT 'natural',
                activo TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS facturas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero VARCHAR(25) UNIQUE NOT NULL,
                fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
                cliente_id INT DEFAULT NULL,
                usuario_id INT DEFAULT NULL,
                subtotal DECIMAL(10,2) DEFAULT 0.00,
                iva DECIMAL(10,2) DEFAULT 0.00,
                descuento DECIMAL(10,2) DEFAULT 0.00,
                total DECIMAL(10,2) DEFAULT 0.00,
                forma_pago VARCHAR(100) DEFAULT 'Efectivo',
                tipo_comprobante ENUM('factura','recibo') DEFAULT 'factura',
                estado ENUM('activa','anulada') DEFAULT 'activa',
                observaciones TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE SET NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            ) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS detalle_facturas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                factura_id INT NOT NULL,
                producto_id INT NOT NULL,
                descripcion VARCHAR(255) NOT NULL,
                cantidad INT NOT NULL DEFAULT 1,
                precio_unitario DECIMAL(10,2) NOT NULL,
                tiene_iva TINYINT(1) DEFAULT 1,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE,
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            ) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS cierre_caja (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fecha DATE NOT NULL,
                usuario_id INT DEFAULT NULL,
                total_efectivo DECIMAL(10,2) DEFAULT 0.00,
                total_tarjeta DECIMAL(10,2) DEFAULT 0.00,
                total_otros DECIMAL(10,2) DEFAULT 0.00,
                total_general DECIMAL(10,2) DEFAULT 0.00,
                num_facturas INT DEFAULT 0,
                observaciones TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            ) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS egresos_caja (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fecha DATE NOT NULL,
                concepto VARCHAR(255) NOT NULL,
                monto DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                metodo_pago ENUM('efectivo','transferencia','otro') DEFAULT 'efectivo',
                observacion TEXT,
                usuario_id INT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            ) ENGINE=InnoDB""",
            """CREATE TABLE IF NOT EXISTS egresos_inventario (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fecha DATE NOT NULL,
                producto_id INT NOT NULL,
                cantidad INT NOT NULL DEFAULT 1,
                motivo ENUM('merma','autoconsumo','dano','otro') DEFAULT 'merma',
                observacion TEXT,
                usuario_id INT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_id) REFERENCES productos(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
            ) ENGINE=InnoDB"""
        ]
        for sql in sqls:
            cur.execute(sql)

    def _insert_defaults(self, cur):
        pw = hashlib.sha256(config.ADMIN_DEFAULT['password'].encode()).hexdigest()
        cur.execute(
            "INSERT IGNORE INTO usuarios (nombre, usuario, password, rol) VALUES (%s, %s, %s, 'admin')",
            (config.ADMIN_DEFAULT['nombre'], config.ADMIN_DEFAULT['usuario'], pw)
        )
        cur.execute(
            "INSERT IGNORE INTO clientes (cedula, nombre, apellido, tipo) VALUES ('9999999999','CONSUMIDOR','FINAL','natural')"
        )
        cats = [
            ('Viveres', 'Productos de primera necesidad'),
            ('Bebidas', 'Bebidas y liquidos'),
            ('Lacteos', 'Productos lacteos'),
            ('Carnes', 'Carnes y embutidos'),
            ('Limpieza', 'Articulos de limpieza'),
            ('Otros', 'Otros productos'),
        ]
        cur.executemany("INSERT IGNORE INTO categorias (nombre, descripcion) VALUES (%s,%s)", cats)
        # Productos de muestra
        products = [
            ('7861058229804', 'Leche entera 1 litro', 1, 0.80, 1.25, 1.10, 50, 10, 0),
            ('7804320568300', 'Arroz blanco 1 kg', 1, 0.60, 0.90, 0.80, 100, 20, 0),
            ('7861058209561', 'Aceite vegetal 1 litro', 1, 1.50, 2.50, 2.20, 30, 5, 1),
            ('0214', 'Pan de molde grande', 1, 1.00, 1.75, 1.50, 20, 5, 0),
            ('7804320569307', 'Coca-Cola 600ml', 2, 0.40, 0.75, 0.65, 48, 12, 0),
            ('7861058220146', 'Agua sin gas 500ml', 2, 0.25, 0.50, 0.45, 60, 15, 0),
            ('7862104861252', 'Yogur frutado 200ml', 3, 0.50, 0.90, 0.80, 24, 6, 0),
            ('7804315000402', 'Queso fresco 250g', 3, 1.20, 2.00, 1.80, 15, 5, 1),
            ('08500000194', 'Detergente polvo 1 kg', 5, 1.80, 3.00, 2.70, 20, 5, 1),
            ('7861057109305', 'Papel higienico x4', 5, 1.20, 2.25, 2.00, 30, 8, 1),
        ]
        for p in products:
            try:
                cur.execute(
                    """INSERT IGNORE INTO productos
                    (codigo, descripcion, categoria_id, precio_compra, precio_venta,
                     precio_mayorista, stock, stock_minimo, tiene_iva)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", p
                )
            except Exception:
                pass

    def execute(self, query, params=None, fetch=True):
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            self.cursor.execute(query, params or ())
            if fetch:
                return self.cursor.fetchall()
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"DB Error: {e}")
            if self.connection:
                try:
                    self.connection.rollback()
                except Exception:
                    pass
            return None

    def fetchone(self, query, params=None):
        result = self.execute(query, params)
        if result:
            return result[0]
        return None

    def disconnect(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception:
            pass


db = DatabaseConnection()
