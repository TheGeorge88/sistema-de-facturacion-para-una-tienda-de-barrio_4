<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use App\Models\EgresoCaja;
use App\Models\EgresoInventario;
use App\Models\Producto;

class EgresoController extends Controller
{
    // ── Egresos de Caja ──────────────────────────────────────────────────────

    public function indexCaja(Request $request)
    {
        $fi   = $request->fi ?? now()->format('Y-m-d');
        $ff   = $request->ff ?? now()->format('Y-m-d');
        $rows = DB::table('egresos_caja as ec')
            ->leftJoin('usuarios as u', 'ec.usuario_id', '=', 'u.id')
            ->select('ec.*', 'u.nombre as cajero')
            ->whereBetween('ec.fecha', [$fi, $ff])
            ->orderByDesc('ec.fecha')->orderByDesc('ec.created_at')
            ->get();
        $total = $rows->sum('monto');
        return view('egresos.caja', compact('rows','total','fi','ff'));
    }

    public function storeCaja(Request $request)
    {
        $request->validate([
            'concepto'    => 'required|string|max:255',
            'monto'       => 'required|numeric|min:0.01',
            'metodo_pago' => 'in:efectivo,transferencia,otro',
        ]);
        EgresoCaja::create([
            'fecha'       => now()->format('Y-m-d'),
            'concepto'    => $request->concepto,
            'monto'       => $request->monto,
            'metodo_pago' => $request->metodo_pago ?? 'efectivo',
            'observacion' => $request->observacion,
            'usuario_id'  => session('usuario')['id'],
        ]);
        return back()->with('success', 'Egreso de caja registrado.');
    }

    public function destroyCaja($id)
    {
        EgresoCaja::destroy($id);
        return back()->with('success', 'Egreso eliminado.');
    }

    // ── Egresos de Inventario ────────────────────────────────────────────────

    public function indexInventario(Request $request)
    {
        $fi   = $request->fi ?? now()->format('Y-m-d');
        $ff   = $request->ff ?? now()->format('Y-m-d');
        $rows = DB::table('egresos_inventario as ei')
            ->join('productos as p', 'ei.producto_id', '=', 'p.id')
            ->leftJoin('usuarios as u', 'ei.usuario_id', '=', 'u.id')
            ->select('ei.*', 'p.descripcion as producto', 'p.codigo', 'u.nombre as cajero')
            ->whereBetween('ei.fecha', [$fi, $ff])
            ->orderByDesc('ei.fecha')->orderByDesc('ei.created_at')
            ->get();
        $productos = Producto::where('activo', 1)->orderBy('descripcion')->get();
        return view('egresos.inventario', compact('rows','productos','fi','ff'));
    }

    public function storeInventario(Request $request)
    {
        $request->validate([
            'producto_id' => 'required|exists:productos,id',
            'cantidad'    => 'required|integer|min:1',
            'motivo'      => 'required|in:merma,autoconsumo,dano,otro',
        ]);
        DB::transaction(function () use ($request) {
            EgresoInventario::create([
                'fecha'       => now()->format('Y-m-d'),
                'producto_id' => $request->producto_id,
                'cantidad'    => $request->cantidad,
                'motivo'      => $request->motivo,
                'observacion' => $request->observacion,
                'usuario_id'  => session('usuario')['id'],
            ]);
            DB::statement(
                'UPDATE productos SET stock = GREATEST(0, stock - ?) WHERE id = ?',
                [$request->cantidad, $request->producto_id]
            );
        });
        return back()->with('success', 'Egreso de inventario registrado. Stock actualizado.');
    }

    // ── API: buscar producto (autocomplete) ──────────────────────────────────
    public function buscarProducto(Request $request)
    {
        $q    = $request->q ?? '';
        $rows = DB::table('productos')
            ->select('id','codigo','descripcion','stock')
            ->where('activo', 1)
            ->where(function ($query) use ($q) {
                $query->where('descripcion', 'like', "%$q%")
                      ->orWhere('codigo', 'like', "%$q%");
            })
            ->orderBy('descripcion')
            ->limit(10)->get();
        return response()->json($rows);
    }
}
