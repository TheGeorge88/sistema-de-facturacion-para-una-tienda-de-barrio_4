@extends('layouts.app')
@section('title','Detalle Factura')
@section('content')
<div class="row justify-content-center">
<div class="col-lg-8">
<div class="card">
    <div class="card-header d-flex justify-content-between">
        <span><i class="bi bi-receipt"></i> Factura #{{ $factura->numero }}</span>
        <span class="badge {{ $factura->estado==='activa' ? 'bg-success' : 'bg-danger' }}">
            {{ strtoupper($factura->estado) }}
        </span>
    </div>
    <div class="card-body">
        {{-- Empresa --}}
        <div class="text-center mb-3 p-2 rounded" style="background:#2D2D2D;color:#fff">
            <h5 class="mb-0 fw-bold" style="color:#FF6F00">🍓 {{ config('app.name') }}</h5>
            <small>RUC: 1713175071001 &nbsp;|&nbsp; Sistema de Facturación</small>
        </div>

        <div class="row mb-3">
            {{-- Datos del cliente --}}
            <div class="col-6">
                <table class="table table-sm table-borderless mb-0" style="font-size:.85rem">
                    <tr><td colspan="2" class="fw-bold text-uppercase text-muted pb-0" style="font-size:.7rem">Datos del Cliente</td></tr>
                    <tr>
                        <td class="text-muted pe-2">Nombre:</td>
                        <td class="fw-bold">{{ trim(($factura->cliente?->nombre ?? '') . ' ' . ($factura->cliente?->apellido ?? '')) ?: 'N/A' }}</td>
                    </tr>
                    <tr>
                        <td class="text-muted">Cédula/RUC:</td>
                        <td>{{ $factura->cliente?->cedula ?? '—' }}</td>
                    </tr>
                    @if($factura->cliente?->telefono)
                    <tr>
                        <td class="text-muted">Teléfono:</td>
                        <td>{{ $factura->cliente->telefono }}</td>
                    </tr>
                    @endif
                    @if($factura->cliente?->direccion)
                    <tr>
                        <td class="text-muted">Dirección:</td>
                        <td>{{ $factura->cliente->direccion }}</td>
                    </tr>
                    @endif
                </table>
            </div>
            {{-- Datos de la factura --}}
            <div class="col-6">
                <table class="table table-sm table-borderless mb-0" style="font-size:.85rem">
                    <tr><td colspan="2" class="fw-bold text-uppercase text-muted pb-0" style="font-size:.7rem">Datos del Comprobante</td></tr>
                    <tr>
                        <td class="text-muted pe-2">Fecha:</td>
                        <td class="fw-bold">{{ $factura->fecha?->format('d/m/Y H:i') }}</td>
                    </tr>
                    <tr>
                        <td class="text-muted">Tipo:</td>
                        <td>{{ strtoupper($factura->tipo_comprobante) }}</td>
                    </tr>
                    <tr>
                        <td class="text-muted">Atendido por:</td>
                        <td class="fw-bold" style="color:#FF6F00">{{ $factura->usuario?->nombre ?? '—' }}</td>
                    </tr>
                    <tr>
                        <td class="text-muted">F. de Pago:</td>
                        <td>{{ $factura->forma_pago }}</td>
                    </tr>
                </table>
            </div>
        </div>
        <table class="table table-sm table-bordered">
            <thead><tr>
                <th>Descripción</th><th>Cant</th><th>P.Unit</th><th>Total</th>
            </tr></thead>
            <tbody>
            @foreach($factura->detalles as $d)
            <tr>
                <td>{{ $d->descripcion }} @if($d->tiene_iva)<span class="badge badge-iva">IVA</span>@endif</td>
                <td class="text-center">{{ $d->cantidad }}</td>
                <td class="text-end">${{ number_format($d->precio_unitario,2) }}</td>
                <td class="text-end fw-semibold">${{ number_format($d->subtotal,2) }}</td>
            </tr>
            @endforeach
            </tbody>
        </table>
        <div class="row justify-content-end">
            <div class="col-5">
                <table class="table table-sm">
                    <tr><td>Subtotal:</td><td class="text-end">${{ number_format($factura->subtotal,2) }}</td></tr>
                    <tr><td>IVA 15%:</td><td class="text-end">${{ number_format($factura->iva,2) }}</td></tr>
                    @if($factura->descuento > 0)
                    <tr><td>Descuento:</td><td class="text-end text-danger">-${{ number_format($factura->descuento,2) }}</td></tr>
                    @endif
                    <tr class="fw-bold table-success">
                        <td>TOTAL:</td>
                        <td class="text-end fs-5">${{ number_format($factura->total,2) }}</td>
                    </tr>
                </table>
            </div>
        </div>
        <p class="text-muted small mb-0"><i class="bi bi-info-circle"></i> Estado: <strong>{{ strtoupper($factura->estado) }}</strong></p>
    </div>
    <div class="card-footer">
        <a href="{{ route('facturacion.index') }}" class="btn btn-secondary btn-sm">
            <i class="bi bi-arrow-left"></i> Volver
        </a>
        <button class="btn btn-primary btn-sm ms-2" onclick="window.print()">
            <i class="bi bi-printer"></i> Imprimir
        </button>
    </div>
</div>
</div></div>
@endsection
