<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\{Factura, DetalleFactura};
use Illuminate\Support\Facades\DB;

class ReporteController extends Controller
{
    public function index(Request $request)
    {
        $hoy = now()->toDateString();
        $fecha = $request->get('fecha', $hoy);
        $fecha_ini = $request->get('fecha_ini', now()->subDays(30)->toDateString());
        $fecha_fin = $request->get('fecha_fin', $hoy);

        // Resumen del día
        $resumenDia = Factura::where(DB::raw('DATE(fecha)'), $fecha)
            ->where('estado','activa')
            ->selectRaw('COUNT(*) as num, COALESCE(SUM(subtotal),0) as subtotal,
                         COALESCE(SUM(iva),0) as iva_total,
                         COALESCE(SUM(descuento),0) as descuento,
                         COALESCE(SUM(total),0) as total_ventas')
            ->first();

        $facturasDia = Factura::with('cliente')
            ->where(DB::raw('DATE(fecha)'), $fecha)
            ->where('estado','activa')
            ->orderByDesc('fecha')
            ->get();

        // Período
        $facturasRango = Factura::with('cliente')
            ->whereBetween(DB::raw('DATE(fecha)'), [$fecha_ini, $fecha_fin])
            ->where('estado','activa')
            ->orderByDesc('fecha')
            ->get();

        $totalRango = $facturasRango->sum('total');

        // Más vendidos (período)
        $masVendidos = DetalleFactura::join('facturas','facturas.id','=','detalle_facturas.factura_id')
            ->where('facturas.estado','activa')
            ->whereBetween(DB::raw('DATE(facturas.fecha)'), [$fecha_ini, $fecha_fin])
            ->groupBy('detalle_facturas.producto_id','detalle_facturas.descripcion')
            ->selectRaw('detalle_facturas.descripcion,
                         SUM(detalle_facturas.cantidad) as total_cant,
                         SUM(detalle_facturas.subtotal) as total_ventas')
            ->orderByDesc('total_cant')
            ->limit(20)
            ->get();

        // Cierres
        $cierres = DB::table('cierre_caja')
            ->leftJoin('usuarios','usuarios.id','=','cierre_caja.usuario_id')
            ->select('cierre_caja.*','usuarios.nombre as cajero')
            ->orderByDesc('cierre_caja.fecha')
            ->limit(30)
            ->get();

        return view('reportes.index', compact(
            'fecha','fecha_ini','fecha_fin',
            'resumenDia','facturasDia',
            'facturasRango','totalRango',
            'masVendidos','cierres'
        ));
    }

    public function cerrarCaja(Request $request)
    {
        $hoy = now()->toDateString();
        $r = Factura::where(DB::raw('DATE(fecha)'), $hoy)
            ->where('estado','activa')
            ->selectRaw('COUNT(*) as num, COALESCE(SUM(total),0) as total')
            ->first();

        $egresos = DB::table('egresos_caja')
            ->where('fecha', $hoy)
            ->sum('monto');
        $neto = $r->total - $egresos;

        DB::table('cierre_caja')->insert([
            'fecha'          => $hoy,
            'usuario_id'     => session('usuario.id'),
            'total_efectivo' => $neto,
            'total_tarjeta'  => 0,
            'total_otros'    => 0,
            'total_general'  => $neto,
            'num_facturas'   => $r->num,
            'observaciones'  => $request->get('observaciones',''),
            'created_at'     => now(),
        ]);

        return back()->with('success',
            "Cierre registrado. Ventas: \${$r->total} | Egresos: \${$egresos} | Neto: \${$neto}");
    }
}
