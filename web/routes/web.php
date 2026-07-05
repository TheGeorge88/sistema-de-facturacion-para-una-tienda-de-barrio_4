<?php
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\{
    AuthController, FacturacionController,
    InventarioController, ClienteController,
    ReporteController, UsuarioController,
    EgresoController, CategoriaController
};

// Autenticación
Route::get('/login',  [AuthController::class, 'showLogin'])->name('login');
Route::post('/login', [AuthController::class, 'login']);
Route::post('/logout',[AuthController::class, 'logout'])->name('logout');

Route::get('/', fn() => redirect()->route('facturacion.index'));

// Rutas protegidas
Route::middleware('auth.check')->group(function () {

    // Facturación (core)
    Route::get( '/facturacion',         [FacturacionController::class,'index'])  ->name('facturacion.index');
    Route::post('/facturacion/emitir',  [FacturacionController::class,'emitir']) ->name('facturacion.emitir');
    Route::post('/facturacion/anular',  [FacturacionController::class,'anular']) ->name('facturacion.anular');
    Route::get( '/facturacion/{id}',    [FacturacionController::class,'show'])   ->name('facturacion.show');

    // AJAX helpers
    Route::get('/api/productos/buscar',    [FacturacionController::class,'buscarProducto'])->name('api.productos');
    Route::get('/api/productos/categoria', [FacturacionController::class,'productosPorCategoria'])->name('api.productos.categoria');
    Route::get('/api/clientes/buscar',  [ClienteController::class,    'buscar'])        ->name('api.clientes');

    // Categorías (vista de productos por categoría)
    Route::get('/categorias', [CategoriaController::class, 'index'])->name('categorias.index');
    Route::get('/api/productos/next-code', [InventarioController::class, 'nextCode'])->name('api.next_code');

    // Inventario
    Route::resource('/inventario', InventarioController::class)->names([
        'index'  => 'inventario.index',
        'create' => 'inventario.create',
        'store'  => 'inventario.store',
        'edit'   => 'inventario.edit',
        'update' => 'inventario.update',
        'destroy'=> 'inventario.destroy',
    ]);

    // Clientes
    Route::resource('/clientes', ClienteController::class);

    // Egresos de Caja (RF11)
    Route::get(   '/egresos/caja',       [EgresoController::class,'indexCaja'])     ->name('egresos.caja.index');
    Route::post(  '/egresos/caja',       [EgresoController::class,'storeCaja'])     ->name('egresos.caja.store');
    Route::delete('/egresos/caja/{id}',  [EgresoController::class,'destroyCaja'])   ->name('egresos.caja.destroy');

    // Egresos de Inventario (RF12)
    Route::get( '/egresos/inventario',   [EgresoController::class,'indexInventario'])->name('egresos.inventario.index');
    Route::post('/egresos/inventario',   [EgresoController::class,'storeInventario'])->name('egresos.inventario.store');
    Route::get( '/egresos/buscar-producto', [EgresoController::class,'buscarProducto'])->name('egresos.buscar_producto');

    // Reportes
    Route::get( '/reportes',             [ReporteController::class,'index'])     ->name('reportes.index');
    Route::post('/reportes/cierre-caja', [ReporteController::class,'cerrarCaja'])->name('reportes.cierre');

    // Usuarios (solo admin)
    Route::resource('/usuarios', UsuarioController::class);
});
