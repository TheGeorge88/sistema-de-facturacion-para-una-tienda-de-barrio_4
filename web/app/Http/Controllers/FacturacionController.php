<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\{Factura, DetalleFactura, Producto, Cliente, Categoria};
use Illuminate\Support\Facades\DB;

class FacturacionController extends Controller
{
    public function index()
    {
        $numero     = Factura::siguienteNumero();
        $consumidor = Cliente::where('cedula', '9999999999')->first();
        $categorias = Categoria::orderBy('nombre')->get();
        return response()
            ->view('facturacion.index', compact('numero', 'consumidor', 'categorias'))
            ->header('Cache-Control', 'no-store, no-cache, must-revalidate')
            ->header('Pragma', 'no-cache')
            ->header('Expires', '0');
    }

    public function productosPorCategoria(Request $request)
    {
        $cat = $request->get('cat');
        $productos = Producto::activos()
            ->where('categoria_id', $cat)
            ->select('id','codigo','descripcion','precio_venta','tiene_iva','stock')
            ->orderBy('descripcion')
            ->get();
        return response()->json($productos);
    }

    public function buscarProducto(Request $request)
    {
        $q = $request->get('q', '');
        if (strlen($q) < 1) return response()->json([]);

        $productos = Producto::activos()
            ->where(function ($query) use ($q) {
                $query->where('codigo', 'like', "%$q%")
                      ->orWhere('descripcion', 'like', "%$q%");
            })
            ->select('id','codigo','descripcion','precio_venta','tiene_iva','stock')
            ->limit(15)
            ->get();

        return response()->json($productos);
    }

    public function buscarCliente(Request $request)
    {
        $q = $request->get('q', '');
        if (strlen($q) < 2) return response()->json([]);

        $clientes = Cliente::where('activo', 1)
            ->where(function ($query) use ($q) {
                $query->where('cedula', 'like', "%$q%")
                      ->orWhere('nombre', 'like', "%$q%")
                      ->orWhere('apellido', 'like', "%$q%");
            })
            ->select('id','cedula','nombre','apellido','telefono')
            ->limit(10)
            ->get()
            ->map(fn($c) => [
                'id'      => $c->id,
                'cedula'  => $c->cedula,
                'nombre'  => trim("{$c->nombre} {$c->apellido}"),
                'telefono'=> $c->telefono,
            ]);

        return response()->json($clientes);
    }

    public function emitir(Request $request)
    {
        $request->validate([
            'items'            => 'required|array|min:1',
            'items.*.producto_id' => 'required|integer',
            'items.*.cantidad'    => 'required|integer|min:1',
            'cliente_id'       => 'required|integer',
            'forma_pago'       => 'required|string',
            'tipo_comprobante' => 'required|in:factura,recibo',
        ]);

        DB::beginTransaction();
        try {
            $iva_pct = 15;
            $subtotal = 0;
            $iva_total = 0;
            $descuento = (float) $request->get('descuento', 0);
            $items_db = [];

            foreach ($request->items as $item) {
                $prod = Producto::findOrFail($item['producto_id']);
                $cant = (int) $item['cantidad'];
                $precio = (float) $prod->precio_venta;
                $sub = round($precio * $cant, 2);

                if ($prod->tiene_iva) {
                    $base = round($sub / (1 + $iva_pct / 100), 4);
                    $iva_item = round($sub - $base, 4);
                    $subtotal  += $base;
                    $iva_total += $iva_item;
                } else {
                    $subtotal += $sub;
                }

                $items_db[] = [
                    'producto_id'    => $prod->id,
                    'descripcion'    => $prod->descripcion,
                    'cantidad'       => $cant,
                    'precio_unitario'=> $precio,
                    'tiene_iva'      => $prod->tiene_iva ? 1 : 0,
                    'subtotal'       => $sub,
                ];

                // Descontar stock
                $prod->decrement('stock', $cant);
            }

            $total = round($subtotal + $iva_total - $descuento, 2);

            $factura = Factura::create([
                'numero'           => Factura::siguienteNumero(),
                'fecha'            => now(),
                'cliente_id'       => $request->cliente_id,
                'usuario_id'       => session('usuario.id'),
                'subtotal'         => round($subtotal, 2),
                'iva'              => round($iva_total, 2),
                'descuento'        => $descuento,
                'total'            => $total,
                'forma_pago'       => $request->forma_pago,
                'tipo_comprobante' => $request->tipo_comprobante,
                'estado'           => 'activa',
            ]);

            foreach ($items_db as $it) {
                $it['factura_id'] = $factura->id;
                DetalleFactura::create($it);
            }

            DB::commit();

            $cliente  = \App\Models\Cliente::find($request->cliente_id);
            $cajero   = session('usuario.nombre', '—');

            return response()->json([
                'success'    => true,
                'factura_id' => $factura->id,
                'numero'     => $factura->numero,
                'fecha'      => now()->format('d/m/Y H:i'),
                'tipo'       => strtoupper($request->tipo_comprobante),
                'forma_pago' => $request->forma_pago,
                'cajero'     => $cajero,
                'cliente'    => [
                    'nombre'  => trim(($cliente->nombre ?? '') . ' ' . ($cliente->apellido ?? '')),
                    'cedula'  => $cliente->cedula ?? '',
                    'telefono'=> $cliente->telefono ?? '',
                ],
                'items'      => array_map(fn($it) => [
                    'descripcion'     => $it['descripcion'],
                    'cantidad'        => $it['cantidad'],
                    'precio_unitario' => number_format($it['precio_unitario'], 2),
                    'subtotal'        => number_format($it['subtotal'], 2),
                    'tiene_iva'       => $it['tiene_iva'],
                ], $items_db),
                'subtotal'   => number_format($subtotal, 2),
                'iva'        => number_format($iva_total, 2),
                'descuento'  => number_format($descuento, 2),
                'total'      => number_format($total, 2),
            ]);
        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json(['success' => false, 'error' => $e->getMessage()], 500);
        }
    }

    public function show($id)
    {
        $factura = Factura::with(['cliente', 'usuario', 'detalles'])->findOrFail($id);
        return view('facturacion.show', compact('factura'));
    }

    public function anular(Request $request)
    {
        $factura = Factura::where('numero', $request->numero)->firstOrFail();
        if ($factura->estado === 'anulada') {
            return response()->json(['success' => false, 'error' => 'Ya está anulada.']);
        }
        $factura->update(['estado' => 'anulada']);
        return response()->json(['success' => true]);
    }
}
