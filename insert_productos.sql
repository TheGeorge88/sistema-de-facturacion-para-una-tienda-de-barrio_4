SET FOREIGN_KEY_CHECKS=0;
DELETE FROM detalle_facturas;
DELETE FROM facturas;
DELETE FROM productos;
DELETE FROM categorias;
ALTER TABLE productos AUTO_INCREMENT=1;
ALTER TABLE categorias AUTO_INCREMENT=1;
SET FOREIGN_KEY_CHECKS=1;

INSERT INTO categorias (nombre, descripcion) VALUES
('Alimentos y Abarrotes',     'Granos, aceites, enlatados y abarrotes'),
('Bebidas',                   'Agua, gaseosas, jugos, leche'),
('Productos de Limpieza',     'Detergentes, desinfectantes y aseo del hogar'),
('Higiene Personal',          'Cuidado personal e higiene'),
('Snacks y Dulces',           'Papas fritas, chicles, caramelos y botanas'),
('Congelados y Refrigerados', 'Helados, embutidos, quesos y lacteos frios'),
('Productos Varios',          'Pilas, velas, utiles y articulos varios');

-- Alimentos y Abarrotes (id=1) - IVA 0%
INSERT INTO productos (codigo,descripcion,categoria_id,precio_compra,precio_venta,precio_mayorista,stock,stock_minimo,tiene_iva,activo) VALUES
('ALA001','Arroz blanco 1 kg',1,0.48,0.75,0.65,100,20,0,1),
('ALA002','Azucar blanca 2 kg',1,0.90,1.40,1.20,80,15,0,1),
('ALA003','Sal yodada 1 kg',1,0.20,0.40,0.35,60,10,0,1),
('ALA004','Aceite vegetal 1 litro',1,1.50,2.50,2.20,50,8,0,1),
('ALA005','Fideos spaghetti 400g',1,0.45,0.75,0.65,70,15,0,1),
('ALA006','Harina de trigo 1 kg',1,0.55,0.90,0.80,40,10,0,1),
('ALA007','Lentejas 500g',1,0.60,1.00,0.90,40,10,0,1),
('ALA008','Atun en lata 180g',1,0.80,1.30,1.15,60,12,0,1),
('ALA009','Frijoles negros 500g',1,0.55,0.90,0.80,40,10,0,1),
('ALA010','Galletas de soda 200g',1,0.60,1.00,0.90,50,10,0,1),
('ALA011','Chocolate en polvo 200g',1,1.00,1.75,1.50,30,8,0,1),
('ALA012','Cafe molido 250g',1,1.80,3.00,2.70,25,5,0,1),
('ALA013','Te negro caja 20 sobres',1,0.80,1.40,1.20,30,6,0,1),
('ALA014','Mayonesa 250g',1,1.00,1.70,1.50,30,6,0,1),
('ALA015','Salsa de tomate 400g',1,0.90,1.50,1.30,30,6,0,1),
('ALA016','Mermelada de fresa 250g',1,0.90,1.60,1.40,25,5,0,1),
('ALA017','Mantequilla de mani 400g',1,1.80,3.00,2.70,20,5,0,1),
('ALA018','Avena en hojuelas 400g',1,0.70,1.20,1.05,35,8,0,1);

-- Bebidas (id=2) - agua/jugos/leche sin IVA, gaseosas/energeticas con IVA
INSERT INTO productos (codigo,descripcion,categoria_id,precio_compra,precio_venta,precio_mayorista,stock,stock_minimo,tiene_iva,activo) VALUES
('BEB001','Agua sin gas 500ml',2,0.20,0.45,0.40,120,24,0,1),
('BEB002','Agua sin gas 1.5 litros',2,0.40,0.75,0.65,80,20,0,1),
('BEB003','Gaseosa cola 600ml',2,0.45,0.80,0.70,96,24,1,1),
('BEB004','Gaseosa cola 2 litros',2,0.90,1.50,1.30,48,12,1,1),
('BEB005','Gaseosa naranja 600ml',2,0.45,0.80,0.70,72,18,1,1),
('BEB006','Jugo de naranja 1 litro',2,0.90,1.60,1.40,40,10,0,1),
('BEB007','Jugo de mango 250ml',2,0.45,0.80,0.70,60,15,0,1),
('BEB008','Bebida energetica 250ml',2,0.90,1.75,1.50,48,12,1,1),
('BEB009','Leche entera 1 litro',2,0.80,1.25,1.10,80,20,0,1),
('BEB010','Yogurt de fresa 200g',2,0.55,0.95,0.85,40,10,0,1),
('BEB011','Yogurt natural 1 litro',2,1.50,2.50,2.20,25,6,0,1),
('BEB012','Leche de chocolate 200ml',2,0.55,0.95,0.85,40,10,0,1);

-- Limpieza (id=3) - IVA 12%
INSERT INTO productos (codigo,descripcion,categoria_id,precio_compra,precio_venta,precio_mayorista,stock,stock_minimo,tiene_iva,activo) VALUES
('LIM001','Jabon de lavar ropa barra',3,0.50,0.90,0.80,60,12,1,1),
('LIM002','Detergente en polvo 1 kg',3,1.80,3.00,2.70,40,8,1,1),
('LIM003','Detergente liquido 500ml',3,1.50,2.50,2.20,30,6,1,1),
('LIM004','Suavizante de ropa 1 litro',3,1.40,2.40,2.10,30,6,1,1),
('LIM005','Cloro desinfectante 1 litro',3,0.70,1.20,1.05,40,8,1,1),
('LIM006','Desinfectante pino 1 litro',3,0.90,1.60,1.40,35,8,1,1),
('LIM007','Lavavajillas liquido 500ml',3,0.90,1.60,1.40,30,6,1,1),
('LIM008','Esponjas x2 unidades',3,0.45,0.80,0.70,40,10,1,1),
('LIM009','Escoba plastica',3,2.50,4.50,4.00,15,3,1,1),
('LIM010','Trapeador algodon',3,2.80,5.00,4.50,10,2,1,1);

-- Higiene Personal (id=4) - IVA 12%
INSERT INTO productos (codigo,descripcion,categoria_id,precio_compra,precio_venta,precio_mayorista,stock,stock_minimo,tiene_iva,activo) VALUES
('HIG001','Papel higienico x4 rollos',4,1.20,2.25,2.00,50,10,1,1),
('HIG002','Papel higienico x12 rollos',4,3.00,5.50,5.00,30,6,1,1),
('HIG003','Pasta dental 90ml',4,0.90,1.60,1.40,35,8,1,1),
('HIG004','Cepillo de dientes adulto',4,0.70,1.25,1.10,30,6,1,1),
('HIG005','Jabon de bano 90g',4,0.45,0.80,0.70,60,12,1,1),
('HIG006','Shampoo 400ml',4,2.00,3.75,3.30,25,5,1,1),
('HIG007','Acondicionador 400ml',4,2.00,3.75,3.30,20,4,1,1),
('HIG008','Desodorante spray 150ml',4,1.80,3.25,2.90,25,5,1,1),
('HIG009','Toallas sanitarias x10',4,1.50,2.75,2.50,30,6,1,1),
('HIG010','Panales bebe talla M x20',4,5.50,9.50,8.50,20,4,1,1),
('HIG011','Alcohol antiseptico 250ml',4,0.80,1.50,1.30,35,8,1,1),
('HIG012','Curitas x10 unidades',4,0.50,0.90,0.80,30,6,1,1);

-- Snacks y Dulces (id=5) - IVA 12%
INSERT INTO productos (codigo,descripcion,categoria_id,precio_compra,precio_venta,precio_mayorista,stock,stock_minimo,tiene_iva,activo) VALUES
('SNA001','Papas fritas bolsa 40g',5,0.35,0.65,0.58,80,20,1,1),
('SNA002','Papas fritas bolsa 120g',5,0.80,1.50,1.30,50,12,1,1),
('SNA003','Chicles x5 unidades',5,0.10,0.25,0.20,100,25,1,1),
('SNA004','Caramelos surtidos 100g',5,0.55,1.00,0.90,50,10,1,1),
('SNA005','Mani tostado con sal 100g',5,0.55,1.00,0.90,60,15,1,1),
('SNA006','Barra de chocolate 45g',5,0.70,1.25,1.10,60,15,1,1),
('SNA007','Palomitas de maiz 50g',5,0.45,0.85,0.75,40,10,1,1);

-- Congelados y Refrigerados (id=6)
INSERT INTO productos (codigo,descripcion,categoria_id,precio_compra,precio_venta,precio_mayorista,stock,stock_minimo,tiene_iva,activo) VALUES
('CON001','Helado de vainilla 1 litro',6,2.50,4.50,4.00,20,4,1,1),
('CON002','Helado paleta x6 unidades',6,1.50,2.75,2.50,30,6,1,1),
('CON003','Salchichas paquete 500g',6,2.00,3.50,3.10,20,4,1,1),
('CON004','Queso fresco 250g',6,1.20,2.10,1.90,25,5,0,1),
('CON005','Mantequilla 250g',6,1.30,2.25,2.00,20,5,0,1),
('CON006','Carne de res empacada 500g',6,3.00,5.50,5.00,15,3,0,1);

-- Productos Varios (id=7) - IVA 12% excepto recargas
INSERT INTO productos (codigo,descripcion,categoria_id,precio_compra,precio_venta,precio_mayorista,stock,stock_minimo,tiene_iva,activo) VALUES
('VAR001','Pilas AA x2 unidades',7,0.55,1.00,0.90,40,8,1,1),
('VAR002','Pilas AAA x2 unidades',7,0.55,1.00,0.90,40,8,1,1),
('VAR003','Velas blancas x6 unidades',7,0.60,1.10,1.00,30,6,1,1),
('VAR004','Fosforos caja',7,0.15,0.30,0.25,60,12,1,1),
('VAR005','Bolsas de basura x10 grandes',7,0.70,1.25,1.10,35,8,1,1),
('VAR006','Cuaderno universitario 100h',7,0.80,1.50,1.30,30,6,1,1),
('VAR007','Recarga telefonica Claro $1',7,1.00,1.00,1.00,99,10,0,1),
('VAR008','Recarga telefonica CNT $2',7,2.00,2.00,2.00,99,10,0,1),
('VAR009','Bolsas plasticas x50',7,0.30,0.60,0.50,50,10,1,1),
('VAR010','Cinta adhesiva transparente',7,0.45,0.85,0.75,25,5,1,1);

SELECT 'Categorias:' AS info, COUNT(*) AS total FROM categorias
UNION ALL
SELECT 'Productos:', COUNT(*) FROM productos;
