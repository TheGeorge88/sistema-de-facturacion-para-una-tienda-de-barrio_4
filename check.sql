SELECT 'categorias' AS tabla, COUNT(*) AS total FROM categorias
UNION ALL
SELECT 'productos', COUNT(*) FROM productos;
