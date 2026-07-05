import sys
sys.path.insert(0, '.')
from database.connection import db

print("Eliminando datos anteriores...")
db.execute('SET FOREIGN_KEY_CHECKS=0', fetch=False)
db.execute('DELETE FROM detalle_facturas', fetch=False)
db.execute('DELETE FROM facturas', fetch=False)
db.execute('DELETE FROM productos', fetch=False)
db.execute('DELETE FROM categorias', fetch=False)
db.execute('ALTER TABLE productos AUTO_INCREMENT=1', fetch=False)
db.execute('ALTER TABLE categorias AUTO_INCREMENT=1', fetch=False)
db.execute('SET FOREIGN_KEY_CHECKS=1', fetch=False)
print("Datos anteriores eliminados OK")

# Insertar categorias
categorias = [
    ('Alimentos y Abarrotes',     'Granos, aceites, enlatados y abarrotes'),
    ('Bebidas',                   'Agua, gaseosas, jugos, leche'),
    ('Productos de Limpieza',     'Detergentes, desinfectantes y aseo del hogar'),
    ('Higiene Personal',          'Cuidado personal e higiene'),
    ('Snacks y Dulces',           'Papas fritas, chicles, caramelos y botanas'),
    ('Congelados y Refrigerados', 'Helados, embutidos, quesos y lacteos frios'),
    ('Productos Varios',          'Pilas, velas, utiles y articulos varios'),
]
for cat in categorias:
    db.execute('INSERT INTO categorias (nombre, descripcion) VALUES (%s,%s)', cat, fetch=False)

cats = {r['nombre']: r['id'] for r in db.execute('SELECT id, nombre FROM categorias')}
print(f"Categorias creadas: {len(cats)}")

# (cod, descripcion, categoria, p_compra, p_venta, p_mayor, stock, stock_min, tiene_iva)
productos = [
    # ALIMENTOS Y ABARROTES - IVA 0% (productos basicos Ecuador)
    ('ALA001', 'Arroz blanco 1 kg',             'Alimentos y Abarrotes', 0.48, 0.75, 0.65, 100, 20, 0),
    ('ALA002', 'Azucar blanca 2 kg',            'Alimentos y Abarrotes', 0.90, 1.40, 1.20,  80, 15, 0),
    ('ALA003', 'Sal yodada 1 kg',               'Alimentos y Abarrotes', 0.20, 0.40, 0.35,  60, 10, 0),
    ('ALA004', 'Aceite vegetal 1 litro',        'Alimentos y Abarrotes', 1.50, 2.50, 2.20,  50,  8, 0),
    ('ALA005', 'Fideos spaghetti 400g',         'Alimentos y Abarrotes', 0.45, 0.75, 0.65,  70, 15, 0),
    ('ALA006', 'Harina de trigo 1 kg',          'Alimentos y Abarrotes', 0.55, 0.90, 0.80,  40, 10, 0),
    ('ALA007', 'Lentejas 500g',                 'Alimentos y Abarrotes', 0.60, 1.00, 0.90,  40, 10, 0),
    ('ALA008', 'Atun en lata 180g',             'Alimentos y Abarrotes', 0.80, 1.30, 1.15,  60, 12, 0),
    ('ALA009', 'Frijoles negros 500g',          'Alimentos y Abarrotes', 0.55, 0.90, 0.80,  40, 10, 0),
    ('ALA010', 'Galletas de soda 200g',         'Alimentos y Abarrotes', 0.60, 1.00, 0.90,  50, 10, 0),
    ('ALA011', 'Chocolate en polvo 200g',       'Alimentos y Abarrotes', 1.00, 1.75, 1.50,  30,  8, 0),
    ('ALA012', 'Cafe molido 250g',              'Alimentos y Abarrotes', 1.80, 3.00, 2.70,  25,  5, 0),
    ('ALA013', 'Te negro caja 20 sobres',       'Alimentos y Abarrotes', 0.80, 1.40, 1.20,  30,  6, 0),
    ('ALA014', 'Mayonesa 250g',                 'Alimentos y Abarrotes', 1.00, 1.70, 1.50,  30,  6, 0),
    ('ALA015', 'Salsa de tomate 400g',          'Alimentos y Abarrotes', 0.90, 1.50, 1.30,  30,  6, 0),
    ('ALA016', 'Mermelada de fresa 250g',       'Alimentos y Abarrotes', 0.90, 1.60, 1.40,  25,  5, 0),
    ('ALA017', 'Mantequilla de mani 400g',      'Alimentos y Abarrotes', 1.80, 3.00, 2.70,  20,  5, 0),
    ('ALA018', 'Avena en hojuelas 400g',        'Alimentos y Abarrotes', 0.70, 1.20, 1.05,  35,  8, 0),
    # BEBIDAS
    ('BEB001', 'Agua sin gas 500ml',            'Bebidas', 0.20, 0.45, 0.40, 120, 24, 0),
    ('BEB002', 'Agua sin gas 1.5 litros',       'Bebidas', 0.40, 0.75, 0.65,  80, 20, 0),
    ('BEB003', 'Gaseosa cola 600ml',            'Bebidas', 0.45, 0.80, 0.70,  96, 24, 1),
    ('BEB004', 'Gaseosa cola 2 litros',         'Bebidas', 0.90, 1.50, 1.30,  48, 12, 1),
    ('BEB005', 'Gaseosa naranja 600ml',         'Bebidas', 0.45, 0.80, 0.70,  72, 18, 1),
    ('BEB006', 'Jugo de naranja 1 litro',       'Bebidas', 0.90, 1.60, 1.40,  40, 10, 0),
    ('BEB007', 'Jugo de mango 250ml',           'Bebidas', 0.45, 0.80, 0.70,  60, 15, 0),
    ('BEB008', 'Bebida energetica 250ml',       'Bebidas', 0.90, 1.75, 1.50,  48, 12, 1),
    ('BEB009', 'Leche entera 1 litro',          'Bebidas', 0.80, 1.25, 1.10,  80, 20, 0),
    ('BEB010', 'Yogurt de fresa 200g',          'Bebidas', 0.55, 0.95, 0.85,  40, 10, 0),
    ('BEB011', 'Yogurt natural 1 litro',        'Bebidas', 1.50, 2.50, 2.20,  25,  6, 0),
    ('BEB012', 'Leche de chocolate 200ml',      'Bebidas', 0.55, 0.95, 0.85,  40, 10, 0),
    # LIMPIEZA - IVA 12%
    ('LIM001', 'Jabon de lavar ropa barra',     'Productos de Limpieza', 0.50, 0.90, 0.80, 60, 12, 1),
    ('LIM002', 'Detergente en polvo 1 kg',      'Productos de Limpieza', 1.80, 3.00, 2.70, 40,  8, 1),
    ('LIM003', 'Detergente liquido 500ml',      'Productos de Limpieza', 1.50, 2.50, 2.20, 30,  6, 1),
    ('LIM004', 'Suavizante de ropa 1 litro',    'Productos de Limpieza', 1.40, 2.40, 2.10, 30,  6, 1),
    ('LIM005', 'Cloro desinfectante 1 litro',   'Productos de Limpieza', 0.70, 1.20, 1.05, 40,  8, 1),
    ('LIM006', 'Desinfectante pino 1 litro',    'Productos de Limpieza', 0.90, 1.60, 1.40, 35,  8, 1),
    ('LIM007', 'Lavavajillas liquido 500ml',    'Productos de Limpieza', 0.90, 1.60, 1.40, 30,  6, 1),
    ('LIM008', 'Esponjas x2 unidades',          'Productos de Limpieza', 0.45, 0.80, 0.70, 40, 10, 1),
    ('LIM009', 'Escoba plastica',               'Productos de Limpieza', 2.50, 4.50, 4.00, 15,  3, 1),
    ('LIM010', 'Trapeador algodon',             'Productos de Limpieza', 2.80, 5.00, 4.50, 10,  2, 1),
    # HIGIENE PERSONAL - IVA 12%
    ('HIG001', 'Papel higienico x4 rollos',     'Higiene Personal', 1.20, 2.25, 2.00, 50, 10, 1),
    ('HIG002', 'Papel higienico x12 rollos',    'Higiene Personal', 3.00, 5.50, 5.00, 30,  6, 1),
    ('HIG003', 'Pasta dental 90ml',             'Higiene Personal', 0.90, 1.60, 1.40, 35,  8, 1),
    ('HIG004', 'Cepillo de dientes adulto',     'Higiene Personal', 0.70, 1.25, 1.10, 30,  6, 1),
    ('HIG005', 'Jabon de bano 90g',             'Higiene Personal', 0.45, 0.80, 0.70, 60, 12, 1),
    ('HIG006', 'Shampoo 400ml',                 'Higiene Personal', 2.00, 3.75, 3.30, 25,  5, 1),
    ('HIG007', 'Acondicionador 400ml',          'Higiene Personal', 2.00, 3.75, 3.30, 20,  4, 1),
    ('HIG008', 'Desodorante spray 150ml',       'Higiene Personal', 1.80, 3.25, 2.90, 25,  5, 1),
    ('HIG009', 'Toallas sanitarias x10',        'Higiene Personal', 1.50, 2.75, 2.50, 30,  6, 1),
    ('HIG010', 'Panales bebe talla M x20',      'Higiene Personal', 5.50, 9.50, 8.50, 20,  4, 1),
    ('HIG011', 'Alcohol antiseptico 250ml',     'Higiene Personal', 0.80, 1.50, 1.30, 35,  8, 1),
    ('HIG012', 'Curitas x10 unidades',          'Higiene Personal', 0.50, 0.90, 0.80, 30,  6, 1),
    # SNACKS Y DULCES - IVA 12%
    ('SNA001', 'Papas fritas bolsa 40g',        'Snacks y Dulces', 0.35, 0.65, 0.58, 80, 20, 1),
    ('SNA002', 'Papas fritas bolsa 120g',       'Snacks y Dulces', 0.80, 1.50, 1.30, 50, 12, 1),
    ('SNA003', 'Chicles x5 unidades',           'Snacks y Dulces', 0.10, 0.25, 0.20,100, 25, 1),
    ('SNA004', 'Caramelos surtidos 100g',       'Snacks y Dulces', 0.55, 1.00, 0.90, 50, 10, 1),
    ('SNA005', 'Mani tostado con sal 100g',     'Snacks y Dulces', 0.55, 1.00, 0.90, 60, 15, 1),
    ('SNA006', 'Barra de chocolate 45g',        'Snacks y Dulces', 0.70, 1.25, 1.10, 60, 15, 1),
    ('SNA007', 'Palomitas de maiz 50g',         'Snacks y Dulces', 0.45, 0.85, 0.75, 40, 10, 1),
    # CONGELADOS Y REFRIGERADOS
    ('CON001', 'Helado de vainilla 1 litro',    'Congelados y Refrigerados', 2.50, 4.50, 4.00, 20, 4, 1),
    ('CON002', 'Helado paleta x6 unidades',     'Congelados y Refrigerados', 1.50, 2.75, 2.50, 30, 6, 1),
    ('CON003', 'Salchichas paquete 500g',       'Congelados y Refrigerados', 2.00, 3.50, 3.10, 20, 4, 1),
    ('CON004', 'Queso fresco 250g',             'Congelados y Refrigerados', 1.20, 2.10, 1.90, 25, 5, 0),
    ('CON005', 'Mantequilla 250g',              'Congelados y Refrigerados', 1.30, 2.25, 2.00, 20, 5, 0),
    ('CON006', 'Carne de res empacada 500g',    'Congelados y Refrigerados', 3.00, 5.50, 5.00, 15, 3, 0),
    # VARIOS - IVA 12%
    ('VAR001', 'Pilas AA x2 unidades',          'Productos Varios', 0.55, 1.00, 0.90, 40,  8, 1),
    ('VAR002', 'Pilas AAA x2 unidades',         'Productos Varios', 0.55, 1.00, 0.90, 40,  8, 1),
    ('VAR003', 'Velas blancas x6 unidades',     'Productos Varios', 0.60, 1.10, 1.00, 30,  6, 1),
    ('VAR004', 'Fosforos caja',                 'Productos Varios', 0.15, 0.30, 0.25, 60, 12, 1),
    ('VAR005', 'Bolsas de basura x10 grandes',  'Productos Varios', 0.70, 1.25, 1.10, 35,  8, 1),
    ('VAR006', 'Cuaderno universitario 100h',   'Productos Varios', 0.80, 1.50, 1.30, 30,  6, 1),
    ('VAR007', 'Recarga telefonica Claro $1',   'Productos Varios', 1.00, 1.00, 1.00, 99, 10, 0),
    ('VAR008', 'Recarga telefonica CNT $2',     'Productos Varios', 2.00, 2.00, 2.00, 99, 10, 0),
    ('VAR009', 'Bolsas plasticas x50',          'Productos Varios', 0.30, 0.60, 0.50, 50, 10, 1),
    ('VAR010', 'Cinta adhesiva transparente',   'Productos Varios', 0.45, 0.85, 0.75, 25,  5, 1),
]

insertados = 0
for p in productos:
    cod, desc, cat_name, pc, pv, pm, stk, smin, iva = p
    cat_id = cats.get(cat_name)
    try:
        db.execute(
            'INSERT INTO productos (codigo,descripcion,categoria_id,precio_compra,precio_venta,precio_mayorista,stock,stock_minimo,tiene_iva,activo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1)',
            (cod, desc, cat_id, pc, pv, pm, stk, smin, iva), fetch=False
        )
        insertados += 1
    except Exception as e:
        print(f'  Error en {cod}: {e}')

total = db.fetchone('SELECT COUNT(*) as n FROM productos')['n']
print(f'Productos insertados: {insertados}')
print(f'Total en base de datos: {total}')
print()
for cat_name in cats:
    n = db.fetchone(f'SELECT COUNT(*) as n FROM productos p JOIN categorias c ON p.categoria_id=c.id WHERE c.nombre=%s', (cat_name,))['n']
    print(f'  {cat_name}: {n} productos')
