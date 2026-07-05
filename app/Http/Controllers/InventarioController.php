<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\{Producto, Categoria};

class InventarioController extends Controller
{
    public function index()
    {
        $productos  = Producto::with('categoria')->where('activo', 1)->orderBy('descripcion')->get();
        $stockBajo  = Producto::activos()->whereColumn('stock', '<=', 'stock_minimo')->count();
        return view('inventario.index', compact('productos', 'stockBajo'));
    }

    public function create()
    {
        $categorias = Categoria::orderBy('nombre')->get();
        return view('inventario.form', compact('categorias'));
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'codigo'          => 'required|string|unique:productos,codigo',
            'descripcion'     => 'required|string|max:255',
            'categoria_id'    => 'nullable|integer',
            'precio_compra'   => 'required|numeric|min:0',
            'precio_venta'    => 'required|numeric|min:0',
            'precio_mayorista'=> 'required|numeric|min:0',
            'stock'           => 'required|integer|min:0',
            'stock_minimo'    => 'required|integer|min:0',
            'tiene_iva'       => 'nullable',
        ]);
        $data['tiene_iva'] = $request->has('tiene_iva') ? 1 : 0;
        $data['activo']    = 1;
        Producto::create($data);
        return redirect()->route('inventario.index')->with('success', 'Producto creado correctamente.');
    }

    public function edit(string $id)
    {
        $producto   = Producto::findOrFail($id);
        $categorias = Categoria::orderBy('nombre')->get();
        return view('inventario.form', compact('producto', 'categorias'));
    }

    public function update(Request $request, string $id)
    {
        $producto = Producto::findOrFail($id);
        $data = $request->validate([
            'codigo'          => "required|string|unique:productos,codigo,$id",
            'descripcion'     => 'required|string|max:255',
            'categoria_id'    => 'nullable|integer',
            'precio_compra'   => 'required|numeric|min:0',
            'precio_venta'    => 'required|numeric|min:0',
            'precio_mayorista'=> 'required|numeric|min:0',
            'stock'           => 'required|integer|min:0',
            'stock_minimo'    => 'required|integer|min:0',
        ]);
        $data['tiene_iva'] = $request->has('tiene_iva') ? 1 : 0;
        $producto->update($data);
        return redirect()->route('inventario.index')->with('success', 'Producto actualizado.');
    }

    public function destroy(string $id)
    {
        Producto::findOrFail($id)->update(['activo' => 0]);
        return redirect()->route('inventario.index')->with('success', 'Producto eliminado.');
    }

    public function show(string $id) { return redirect()->route('inventario.edit', $id); }

    public function nextCode(Request $request)
    {
        $prefix = strtoupper($request->get('prefix', 'PRD'));
        $last   = Producto::where('codigo', 'like', $prefix . '%')
            ->orderByRaw('LENGTH(codigo) DESC, codigo DESC')
            ->value('codigo');
        if ($last) {
            $num = intval(substr($last, strlen($prefix))) + 1;
        } else {
            $num = 1;
        }
        return response()->json(['code' => $prefix . str_pad($num, 3, '0', STR_PAD_LEFT)]);
    }
}
