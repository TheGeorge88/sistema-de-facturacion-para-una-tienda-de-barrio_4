@extends('layouts.app')
@section('title','Egresos de Caja')
@section('content')
<div class="container-fluid py-3">

  {{-- Sub-nav --}}
  <ul class="nav nav-tabs mb-3">
    <li class="nav-item">
      <a class="nav-link active" href="{{ route('egresos.caja.index') }}">
        <i class="bi bi-cash-stack"></i> Egresos de Caja
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link" href="{{ route('egresos.inventario.index') }}">
        <i class="bi bi-box-arrow-down"></i> Merma / Inventario
      </a>
    </li>
  </ul>

  {{-- Alertas --}}
  @if(session('success'))
    <div class="alert alert-success alert-dismissible fade show py-2" role="alert">
      {{ session('success') }}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  @endif

  <div class="row mb-3">
    <div class="col">
      <h5 class="fw-bold text-danger mb-0"><i class="bi bi-cash-stack"></i> Egresos de Caja (RF11)</h5>
    </div>
  </div>

  <div class="row g-3">
    {{-- Formulario --}}
    <div class="col-lg-4">
      <div class="card shadow-sm border-0">
        <div class="card-header bg-danger text-white fw-bold py-2">
          Registrar Egreso
        </div>
        <div class="card-body">
          <form action="{{ route('egresos.caja.store') }}" method="POST">
            @csrf
            <div class="mb-3">
              <label class="form-label fw-semibold">Concepto / Descripción <span class="text-danger">*</span></label>
              <input type="text" name="concepto" class="form-control @error('concepto') is-invalid @enderror"
                     value="{{ old('concepto') }}" placeholder="Ej: Pago proveedor, gasto limpieza..." required>
              @error('concepto')<div class="invalid-feedback">{{ $message }}</div>@enderror
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label fw-semibold">Monto ($) <span class="text-danger">*</span></label>
                <input type="number" name="monto" step="0.01" min="0.01"
                       class="form-control @error('monto') is-invalid @enderror"
                       value="{{ old('monto') }}" required>
                @error('monto')<div class="invalid-feedback">{{ $message }}</div>@enderror
              </div>
              <div class="col-6">
                <label class="form-label fw-semibold">Método de Pago</label>
                <select name="metodo_pago" class="form-select">
                  <option value="efectivo">Efectivo</option>
                  <option value="transferencia">Transferencia</option>
                  <option value="otro">Otro</option>
                </select>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold">Observación</label>
              <textarea name="observacion" class="form-control" rows="2"
                        placeholder="Opcional...">{{ old('observacion') }}</textarea>
            </div>
            <button type="submit" class="btn btn-danger w-100 fw-bold">
              <i class="bi bi-plus-circle"></i> REGISTRAR EGRESO
            </button>
          </form>
        </div>
      </div>
    </div>

    {{-- Historial --}}
    <div class="col-lg-8">
      <div class="card shadow-sm border-0">
        <div class="card-header bg-light d-flex justify-content-between align-items-center py-2">
          <span class="fw-bold">Historial de Egresos</span>
          <form class="d-flex gap-2 align-items-center" method="GET">
            <input type="date" name="fi" value="{{ $fi }}" class="form-control form-control-sm" style="width:140px">
            <span>–</span>
            <input type="date" name="ff" value="{{ $ff }}" class="form-control form-control-sm" style="width:140px">
            <button type="submit" class="btn btn-sm btn-secondary">Filtrar</button>
          </form>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-sm table-hover mb-0">
              <thead class="table-dark">
                <tr>
                  <th>#</th><th>Fecha</th><th>Concepto</th><th>Monto</th>
                  <th>Método</th><th>Cajero</th><th></th>
                </tr>
              </thead>
              <tbody>
                @forelse($rows as $e)
                <tr>
                  <td>{{ $e->id }}</td>
                  <td>{{ $e->fecha }}</td>
                  <td>{{ $e->concepto }}</td>
                  <td class="fw-bold text-danger">${{ number_format($e->monto,2) }}</td>
                  <td><span class="badge bg-secondary">{{ $e->metodo_pago }}</span></td>
                  <td>{{ $e->cajero ?? '—' }}</td>
                  <td>
                    <form action="{{ route('egresos.caja.destroy', $e->id) }}" method="POST"
                          onsubmit="return confirm('¿Eliminar este egreso?')">
                      @csrf @method('DELETE')
                      <button class="btn btn-sm btn-outline-danger py-0 px-1">
                        <i class="bi bi-trash"></i>
                      </button>
                    </form>
                  </td>
                </tr>
                @empty
                <tr><td colspan="7" class="text-center text-muted py-3">Sin egresos en el período</td></tr>
                @endforelse
              </tbody>
              <tfoot class="table-light">
                <tr>
                  <th colspan="3" class="text-end">TOTAL</th>
                  <th class="text-danger">${{ number_format($total,2) }}</th>
                  <th colspan="3"></th>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
@endsection
