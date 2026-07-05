@extends('layouts.app')
@section('title','Reportes')
@section('content')

{{-- Tabs --}}
<ul class="nav nav-tabs mb-3" id="reporteTabs">
    <li class="nav-item">
        <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tab-dia">
            <i class="bi bi-calendar-day"></i> Ventas del Día
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-rango">
            <i class="bi bi-calendar-range"></i> Por Período
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-vendidos">
            <i class="bi bi-bar-chart"></i> Más Vendidos
        </button>
    </li>
    <li class="nav-item">
        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-cierre">
            <i class="bi bi-cash-coin"></i> Cierre de Caja
        </button>
    </li>
</ul>

<div class="tab-content">

    {{-- Tab Día --}}
    <div class="tab-pane fade show active" id="tab-dia">
        <form class="row g-2 mb-3 align-items-end">
            <div class="col-auto">
                <label class="form-label mb-1 small">Fecha</label>
                <input type="date" name="fecha" class="form-control form-control-sm"
                       value="{{ $fecha }}">
            </div>
            <div class="col-auto">
                <button class="btn btn-primary btn-sm">Consultar</button>
            </div>
        </form>

        {{-- Tarjetas resumen --}}
        <div class="row g-3 mb-3">
            @foreach([
                ['Facturas',    $resumenDia->num ?? 0,                           'primary', 'receipt'],
                ['Subtotal',    '$ '.number_format($resumenDia->subtotal??0,2),  'info',    'calculator'],
                ['IVA 12%',     '$ '.number_format($resumenDia->iva_total??0,2), 'warning', 'percent'],
                ['TOTAL',       '$ '.number_format($resumenDia->total_ventas??0,2),'success','cash-stack'],
            ] as [$label, $val, $color, $icon])
            <div class="col-6 col-md-3">
                <div class="card text-white bg-{{ $color }}">
                    <div class="card-body py-3 text-center">
                        <i class="bi bi-{{ $icon }} fs-4"></i>
                        <p class="mb-0 small">{{ $label }}</p>
                        <p class="fs-5 fw-bold mb-0">{{ $val }}</p>
                    </div>
                </div>
            </div>
            @endforeach
        </div>

        <div class="card">
            <div class="card-header">Facturas del {{ $fecha }}</div>
            <div class="card-body p-2 table-wrap">
                <table class="table table-sm table-bordered mb-0">
                    <thead><tr>
                        <th>N° Factura</th><th>Hora</th><th>Cliente</th>
                        <th>Subtotal</th><th>IVA</th><th>Total</th><th>Pago</th><th>Estado</th>
                    </tr></thead>
                    <tbody>
                    @forelse($facturasDia as $f)
                    <tr class="{{ $f->estado==='anulada' ? 'table-danger text-muted' : '' }}">
                        <td>{{ $f->numero }}</td>
                        <td>{{ $f->fecha?->format('H:i') }}</td>
                        <td>{{ $f->cliente?->nombre_completo ?? 'Consumidor Final' }}</td>
                        <td class="text-end">${{ number_format($f->subtotal,2) }}</td>
                        <td class="text-end">${{ number_format($f->iva,2) }}</td>
                        <td class="text-end fw-semibold">${{ number_format($f->total,2) }}</td>
                        <td>{{ $f->forma_pago }}</td>
                        <td><span class="badge {{ $f->estado==='activa'?'bg-success':'bg-danger' }}">
                            {{ strtoupper($f->estado) }}</span></td>
                    </tr>
                    @empty
                    <tr><td colspan="8" class="text-center py-2 text-muted">Sin facturas ese día</td></tr>
                    @endforelse
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    {{-- Tab Período --}}
    <div class="tab-pane fade" id="tab-rango">
        <form class="row g-2 mb-3 align-items-end">
            <div class="col-auto">
                <label class="form-label mb-1 small">Desde</label>
                <input type="date" name="fecha_ini" class="form-control form-control-sm"
                       value="{{ $fecha_ini }}">
            </div>
            <div class="col-auto">
                <label class="form-label mb-1 small">Hasta</label>
                <input type="date" name="fecha_fin" class="form-control form-control-sm"
                       value="{{ $fecha_fin }}">
            </div>
            <div class="col-auto">
                <button class="btn btn-primary btn-sm">Consultar</button>
            </div>
            <div class="col-auto">
                <span class="badge bg-success fs-6">
                    {{ $facturasRango->count() }} fact. — ${{ number_format($totalRango,2) }}
                </span>
            </div>
        </form>
        <div class="card">
            <div class="card-body p-2 table-wrap">
                <table class="table table-sm table-bordered mb-0">
                    <thead><tr>
                        <th>N° Factura</th><th>Fecha</th><th>Cliente</th>
                        <th>Total</th><th>Pago</th>
                    </tr></thead>
                    <tbody>
                    @forelse($facturasRango as $f)
                    <tr>
                        <td><a href="{{ route('facturacion.show',$f->id) }}">{{ $f->numero }}</a></td>
                        <td>{{ $f->fecha?->format('d/m/Y') }}</td>
                        <td>{{ $f->cliente?->nombre_completo ?? '—' }}</td>
                        <td class="text-end fw-semibold">${{ number_format($f->total,2) }}</td>
                        <td>{{ $f->forma_pago }}</td>
                    </tr>
                    @empty
                    <tr><td colspan="5" class="text-center py-2 text-muted">Sin facturas en ese período</td></tr>
                    @endforelse
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    {{-- Tab Más vendidos --}}
    <div class="tab-pane fade" id="tab-vendidos">
        <form class="row g-2 mb-3 align-items-end">
            <div class="col-auto">
                <label class="form-label mb-1 small">Desde</label>
                <input type="date" name="fecha_ini" class="form-control form-control-sm" value="{{ $fecha_ini }}">
            </div>
            <div class="col-auto">
                <label class="form-label mb-1 small">Hasta</label>
                <input type="date" name="fecha_fin" class="form-control form-control-sm" value="{{ $fecha_fin }}">
            </div>
            <div class="col-auto">
                <button class="btn btn-primary btn-sm">Consultar</button>
            </div>
        </form>
        <div class="card">
            <div class="card-body p-2 table-wrap">
                <table class="table table-sm table-bordered mb-0">
                    <thead><tr><th>#</th><th>Descripción</th><th>Unidades</th><th>Total Ventas</th></tr></thead>
                    <tbody>
                    @forelse($masVendidos as $i => $mv)
                    <tr>
                        <td>{{ $i+1 }}</td>
                        <td>{{ $mv->descripcion }}</td>
                        <td class="text-center fw-bold">{{ $mv->total_cant }}</td>
                        <td class="text-end">${{ number_format($mv->total_ventas,2) }}</td>
                    </tr>
                    @empty
                    <tr><td colspan="4" class="text-center py-2 text-muted">Sin datos</td></tr>
                    @endforelse
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    {{-- Tab Cierre --}}
    <div class="tab-pane fade" id="tab-cierre">
        <div class="row g-3">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">Cierre del Día</div>
                    <div class="card-body">
                        <p><strong>Fecha:</strong> {{ now()->format('d/m/Y') }}</p>
                        <p><strong>Facturas:</strong> {{ $resumenDia->num ?? 0 }}</p>
                        <p><strong>Total:</strong> ${{ number_format($resumenDia->total_ventas??0,2) }}</p>
                        <form action="{{ route('reportes.cierre') }}" method="POST">
                            @csrf
                            <div class="mb-3">
                                <label class="form-label small">Observaciones</label>
                                <textarea name="observaciones" class="form-control form-control-sm" rows="2"></textarea>
                            </div>
                            <button class="btn btn-danger w-100"
                                    onclick="return confirm('¿Registrar cierre de caja del día?')">
                                <i class="bi bi-cash-coin"></i> REGISTRAR CIERRE
                            </button>
                        </form>
                    </div>
                </div>
            </div>
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">Historial de Cierres</div>
                    <div class="card-body p-2 table-wrap">
                        <table class="table table-sm table-bordered mb-0">
                            <thead><tr>
                                <th>Fecha</th><th>Cajero</th><th>Efectivo</th>
                                <th>Tarjeta</th><th>Total</th><th># Fact.</th>
                            </tr></thead>
                            <tbody>
                            @forelse($cierres as $cc)
                            <tr>
                                <td>{{ $cc->fecha }}</td>
                                <td>{{ $cc->cajero ?? '—' }}</td>
                                <td class="text-end">${{ number_format($cc->total_efectivo,2) }}</td>
                                <td class="text-end">${{ number_format($cc->total_tarjeta,2) }}</td>
                                <td class="text-end fw-bold">${{ number_format($cc->total_general,2) }}</td>
                                <td class="text-center">{{ $cc->num_facturas }}</td>
                            </tr>
                            @empty
                            <tr><td colspan="6" class="text-center py-2 text-muted">Sin cierres registrados</td></tr>
                            @endforelse
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

</div>
@endsection
