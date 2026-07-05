import os
from dotenv import load_dotenv

load_dotenv()

# Configuracion de la base de datos MySQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'database': os.getenv('DB_NAME', 'facturacion_gg'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'charset': 'utf8mb4',
    'use_unicode': True
}

# Datos de la empresa
EMPRESA = {
    'nombre': 'TUTI FRUT',
    'ruc': '1713175071001',
    'direccion': 'Av. Principal 123, Ciudad',
    'telefono': '0999999999',
    'email': 'tiendagg@gmail.com',
    'ciudad': 'Ecuador'
}

# IVA
IVA_PORCENTAJE = 15

# Numeracion de facturas: prefijo-secuencia
PREFIJO_FACTURA = '001-001-'

# Usuario admin por defecto (password: admin123)
ADMIN_DEFAULT = {
    'nombre': 'Administrador',
    'usuario': 'admin',
    'password': 'admin123'
}
