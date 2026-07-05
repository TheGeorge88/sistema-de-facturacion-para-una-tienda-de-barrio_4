@extends('layouts.app')
@section('title','Categorías')
@section('content')
<div class="container-fluid py-3">

  <div class="row g-3">

    {{-- Panel izquierdo: lista de categorías --}}
    <div class="col-lg-3 col-md-4">
      <div class="card shadow-sm border-0 h-100">
        <div class="card-header fw-bold py-2" style="background:#1a237e;color:white">
          <i class="bi bi-grid-3x3-gap"></i> Categorías
        </div>
        <div class="list-group list-group-flush">
          @foreach($categorias as $cat)
          <a href="{{ route('categorias.index', ['cat' => $cat->id]) }}"
             class="list-group-item list-group-item-action d-flex justify-content-between align-items-center
                    {{ $cat->id == $cat_sel ? 'active' : '' }}">
            {{ $cat->nombre }}
            <span class="badge {{ $cat->id == $cat_sel ? 'bg-white text-dark' : 'bg-primary' }} rounded-pill">
              {{ $cat->productos_count }}
            </span>
          </a>
          @endforeach
        </div>
      </div>
    </div>

    {{-- Panel derecho: productos de la categoría seleccionada --}}
    <div class="col-lg-9 col-md-8">
      @php $catActual = $categorias->firstWhere('id', $cat_sel); @endphp
      <div class="card shadow-sm border-0">
        <div class="card-header d-flex justify-content-between align-items-center py-2"
             style="background:#283593;color:white">
          <span class="fw-bold">
            <i class="bi bi-box-seam"></i>
            {{ $catActual?->nombre ?? 'Productos' }}
            <span class="badge bg-light text-dark ms-2">{{ $productos->count() }}</span>
          </span>
          <a href="{{ route('inventario.create') }}" class="btn btn-sm btn-success fw-bold">
            <i class="bi bi-plus-lg"></i> Nuevo Producto
          </a>
        </div>

        {{-- Buscador dentro de la categoría --}}
        <div class="card-body pb-0 pt-2">
          <input type="text" id="buscar" class="form-control form-control-sm"
                 placeholder="Buscar en {{ $catActual?->nombre }}..."
                 oninput="filtrar(this.value)">
        </div>

        <div class="card-body p-0 mt-2">
          <div class="table-responsive">
            <table class="table table-sm table-hover mb-0" id="tbl">
              <thead class="table-dark">
                <tr>
                  <th>Código</th>
                  <th>Descripción</th>
                  <th class="text-end">P. Compra</th>
                  <th class="text-end">P. Venta</th>
                  <th class="text-end">P. Mayor</th>
                  <th class="text-center">Stock</th>
                  <th class="text-center">IVA</th>
                  <th class="text-center">Acc.</th>
                </tr>
              </thead>
              <tbody>
                @forelse($productos as $p)
                <tr class="{{ $p->stock <= $p->stock_minimo ? 'table-warning' : '' }}">
                  <td><code>{{ $p->codigo }}</code></td>
                  <td>{{ $p->descripcion }}</td>
                  <td class="text-end">${{ number_format($p->precio_compra,2) }}</td>
                  <td class="text-end fw-bold text-success">${{ number_format($p->precio_venta,2) }}</td>
                  <td class="text-end">${{ number_format($p->precio_mayorista,2) }}</td>
                  <td class="text-center {{ $p->stock <= $p->stock_minimo ? 'text-danger fw-bold' : '' }}">
                    {{ $p->stock }}
                    @if($p->stock <= $p->stock_minimo)
                      <i class="bi bi-exclamation-triangle-fill text-danger" title="Stock bajo"></i>
                    @endif
                  </td>
                  <td class="text-center">
                    @if($p->tiene_iva)
                      <span class="badge bg-info text-dark">12%</span>
                    @else
                      <span class="badge bg-secondary">0%</span>
                    @endif
                  </td>
                  <td class="text-center" style="white-space:nowrap">
                    <a href="{{ route('inventario.edit', $p->id) }}"
                       class="btn btn-xs btn-outline-primary py-0 px-1" title="Editar">
                      <i class="bi bi-pencil"></i>
                    </a>
                    <form action="{{ route('inventario.destroy', $p->id) }}" method="POST"
                          class="d-inline"
                          onsubmit="return confirm('¿Eliminar {{ addslashes($p->descripcion) }}?')">
                      @csrf @method('DELETE')
                      <button class="btn btn-xs btn-outline-danger py-0 px-1" title="Eliminar">
                        <i class="bi bi-trash"></i>
                      </button>
                    </form>
                  </td>
                </tr>
                @empty
                <tr>
                  <td colspan="8" class="text-center text-muted py-4">
                    <i class="bi bi-inbox fs-3 d-block mb-1"></i>
                    Sin productos en esta categoría
                  </td>
                </tr>
                @endforelse
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

  </div>
</div>

<script>
function filtrar(q) {
  q = q.toLowerCase();
  document.querySelectorAll('#tbl tbody tr').forEach(tr => {
    tr.style.display = tr.textContent.toLowerCase().includes(q) ? '' : 'none';
  });
}
</script>
@endsection
