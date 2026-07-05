<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Categoria;
use App\Models\Producto;
use Illuminate\Support\Facades\DB;

class CategoriaController extends Controller
{
    public function index(Request $request)
    {
        $categorias = Categoria::withCount(['productos' => fn($q) => $q->where('activo', 1)])
            ->orderBy('nombre')
            ->get();

        $cat_sel = $request->get('cat', $categorias->first()?->id);

        $productos = Producto::where('activo', 1)
            ->where('categoria_id', $cat_sel)
            ->orderBy('descripcion')
            ->get();

        return view('categorias.index', compact('categorias', 'cat_sel', 'productos'));
    }
}
