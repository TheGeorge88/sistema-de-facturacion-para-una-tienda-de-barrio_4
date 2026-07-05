@extends('layouts.app')
@section('title','Inventario')
@section('content')
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <span><i class="bi bi-box-seam"></i> Inventario de Productos ({{ $productos->count() }})</span>
        <div class="d-flex gap-2">
            @if($stockBajo > 0)
            <span class="badge bg-warning text-dark">⚠ Stock bajo: {{ $stockBajo }}</span>
            @endif
            <a href="{{ route('inventario.create') }}" class="btn btn-success btn-sm">
                <i class="bi bi-plus-lg"></i> Nuevo Producto
            </a>
        </div>
    </div>
    <div class="card-body p-2">
        <input type="text" id="inp-filter" class="form-control form-control-sm mb-2"
               placeholder="Filtrar por código o descripción..." oninput="filtrar(this.value)">
        <div class="table-wrap">
        <table class="table table-sm table-bordered table-hover mb-0" id="tbl-prod">
            <thead>
                <tr>
                    <th>Código</th><th>Descripción</th><th>Categoría</th>
                    <th>P.Compra</th><th>P.Venta</th><th>P.Mayor</th>
                    <th>Stock</th><th>Mín</th><th>IVA</th><th>Acc.</th>
                </tr>
            </thead>
            <tbody>
            @forelse($productos as $p)
            <tr class="{{ $p->stock <= $p->stock_minimo ? 'table-warning' : '' }}">
                <td style="font-size:.78rem">{{ $p->codigo }}</td>
                <td>{{ $p->descripcion }}</td>
                <td>{{ $p->categoria?->nombre ?? '—' }}</td>
                <td class="text-end">${{ number_format($p->precio_compra,2) }}</td>
                <td class="text-end fw-semibold">${{ number_format($p->precio_venta,2) }}</td>
                <td class="text-end">${{ number_format($p->precio_mayorista,2) }}</td>
                <td class="text-center {{ $p->stock <= $p->stock_minimo ? 'text-danger fw-bold' : '' }}">
                    {{ $p->stock }}
                </td>
                <td class="text-center">{{ $p->stock_minimo }}</td>
                <td class="text-center">{{ $p->tiene_iva ? '✓' : '' }}</td>
                <td class="text-center" style="white-space:nowrap">
                    <a href="{{ route('inventario.edit', $p->id) }}" class="btn btn-xs btn-outline-primary py-0 px-1">
                        <i class="bi bi-pencil"></i>
                    </a>
                    <form action="{{ route('inventario.destroy', $p->id) }}" method="POST" class="d-inline"
                          onsubmit="return confirm('¿Eliminar {{ addslashes($p->descripcion) }}?')">
                        @csrf @method('DELETE')
                        <button class="btn btn-xs btn-outline-danger py-0 px-1">
                            <i class="bi bi-trash"></i>
                        </button>
                    </form>
                </td>
            </tr>
            @empty
            <tr><td colspan="10" class="text-center py-3 text-muted">Sin productos registrados</td></tr>
            @endforelse
            </tbody>
        </table>
        </div>
    </div>
</div>
@endsection
@push('scripts')
<script>
function filtrar(q) {
    q = q.toLowerCase();
    document.querySelectorAll('#tbl-prod tbody tr').forEach(tr => {
        const txt = tr.textContent.toLowerCase();
        tr.style.display = txt.includes(q) ? '' : 'none';
    });
}
</script>
@endpush
