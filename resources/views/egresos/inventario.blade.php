@extends('layouts.app')
@section('title','Egresos de Inventario')
@section('content')
<div class="container-fluid py-3">

  {{-- Sub-nav --}}
  <ul class="nav nav-tabs mb-3">
    <li class="nav-item">
      <a class="nav-link" href="{{ route('egresos.caja.index') }}">
        <i class="bi bi-cash-stack"></i> Egresos de Caja
      </a>
    </li>
    <li class="nav-item">
      <a class="nav-link active" href="{{ route('egresos.inventario.index') }}">
        <i class="bi bi-box-arrow-down"></i> Merma / Inventario
      </a>
    </li>
  </ul>

  @if(session('success'))
    <div class="alert alert-success alert-dismissible fade show py-2" role="alert">
      {{ session('success') }}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>
  @endif

  <div class="row mb-3">
    <div class="col">
      <h5 class="fw-bold text-warning mb-0"><i class="bi bi-box-arrow-down"></i> Merma / Autoconsumo / Daño (RF12)</h5>
    </div>
  </div>

  <div class="row g-3">
    {{-- Formulario --}}
    <div class="col-lg-4">
      <div class="card shadow-sm border-0">
        <div class="card-header bg-warning text-dark fw-bold py-2">
          Registrar Egreso de Inventario
        </div>
        <div class="card-body">
          <form action="{{ route('egresos.inventario.store') }}" method="POST">
            @csrf
            <div class="mb-3">
              <label class="form-label fw-semibold">Producto <span class="text-danger">*</span></label>
              <input type="text" id="buscar_producto" class="form-control mb-1"
                     placeholder="Escriba código o nombre..." autocomplete="off">
              <input type="hidden" name="producto_id" id="producto_id" value="{{ old('producto_id') }}">
              <div id="lista_productos" class="list-group shadow-sm" style="max-height:160px;overflow-y:auto;display:none"></div>
              <small id="producto_info" class="text-primary fw-semibold"></small>
              @error('producto_id')<div class="text-danger small">{{ $message }}</div>@enderror
            </div>
            <div class="row g-2 mb-3">
              <div class="col-5">
                <label class="form-label fw-semibold">Cantidad <span class="text-danger">*</span></label>
                <input type="number" name="cantidad" class="form-control @error('cantidad') is-invalid @enderror"
                       value="{{ old('cantidad',1) }}" min="1" required>
                @error('cantidad')<div class="invalid-feedback">{{ $message }}</div>@enderror
              </div>
              <div class="col-7">
                <label class="form-label fw-semibold">Motivo <span class="text-danger">*</span></label>
                <select name="motivo" class="form-select @error('motivo') is-invalid @enderror" required>
                  <option value="merma"        {{ old('motivo')=='merma'        ? 'selected':'' }}>Merma</option>
                  <option value="autoconsumo"  {{ old('motivo')=='autoconsumo'  ? 'selected':'' }}>Autoconsumo</option>
                  <option value="dano"         {{ old('motivo')=='dano'         ? 'selected':'' }}>Daño</option>
                  <option value="otro"         {{ old('motivo')=='otro'         ? 'selected':'' }}>Otro</option>
                </select>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label fw-semibold">Observación</label>
              <textarea name="observacion" class="form-control" rows="2">{{ old('observacion') }}</textarea>
            </div>
            <button type="submit" class="btn btn-warning w-100 fw-bold text-dark">
              <i class="bi bi-arrow-down-circle"></i> REGISTRAR EGRESO
            </button>
          </form>
        </div>
      </div>
    </div>

    {{-- Historial --}}
    <div class="col-lg-8">
      <div class="card shadow-sm border-0">
        <div class="card-header bg-light d-flex justify-content-between align-items-center py-2">
          <span class="fw-bold">Historial de Egresos de Inventario</span>
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
                  <th>#</th><th>Fecha</th><th>Código</th><th>Producto</th>
                  <th>Cant.</th><th>Motivo</th><th>Observación</th><th>Cajero</th>
                </tr>
              </thead>
              <tbody>
                @forelse($rows as $e)
                <tr>
                  <td>{{ $e->id }}</td>
                  <td>{{ $e->fecha }}</td>
                  <td><code>{{ $e->codigo }}</code></td>
                  <td>{{ $e->producto }}</td>
                  <td class="fw-bold">{{ $e->cantidad }}</td>
                  <td>
                    @php $badgeColor = match($e->motivo) {
                      'merma'       => 'warning',
                      'autoconsumo' => 'info',
                      'dano'        => 'danger',
                      default       => 'secondary'
                    }; @endphp
                    <span class="badge bg-{{ $badgeColor }}">{{ $e->motivo }}</span>
                  </td>
                  <td class="text-muted small">{{ $e->observacion ?? '—' }}</td>
                  <td>{{ $e->cajero ?? '—' }}</td>
                </tr>
                @empty
                <tr><td colspan="8" class="text-center text-muted py-3">Sin egresos en el período</td></tr>
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
const buscarInput = document.getElementById('buscar_producto');
const lista       = document.getElementById('lista_productos');
const hiddenId    = document.getElementById('producto_id');
const infoLabel   = document.getElementById('producto_info');

buscarInput.addEventListener('input', async function() {
  const q = this.value.trim();
  if (q.length < 2) { lista.style.display='none'; return; }
  const res  = await fetch(`{{ route('egresos.buscar_producto') }}?q=${encodeURIComponent(q)}`);
  const data = await res.json();
  lista.innerHTML = '';
  if (!data.length) { lista.style.display='none'; return; }
  data.forEach(p => {
    const a = document.createElement('a');
    a.href = '#';
    a.className = 'list-group-item list-group-item-action py-1 px-2 small';
    a.textContent = `${p.codigo}  –  ${p.descripcion}  (stock: ${p.stock})`;
    a.addEventListener('click', e => {
      e.preventDefault();
      hiddenId.value    = p.id;
      buscarInput.value = p.descripcion;
      infoLabel.textContent = `Stock actual: ${p.stock}`;
      lista.style.display = 'none';
    });
    lista.appendChild(a);
  });
  lista.style.display = 'block';
});

document.addEventListener('click', e => {
  if (!e.target.closest('#buscar_producto') && !e.target.closest('#lista_productos'))
    lista.style.display = 'none';
});
</script>
@endsection
