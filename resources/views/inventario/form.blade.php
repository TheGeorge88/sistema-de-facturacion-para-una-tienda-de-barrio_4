@extends('layouts.app')
@section('title', isset($producto) ? 'Editar Producto' : 'Nuevo Producto')
@push('styles')
<style>
.sug-box { position:absolute; z-index:2000; background:#fff;
    border:1px solid #c5cae9; border-top:none; border-radius:0 0 8px 8px;
    width:100%; max-height:260px; overflow-y:auto; box-shadow:0 4px 12px rgba(0,0,0,.12); }
.sug-item { padding:8px 14px; cursor:pointer; font-size:.88rem;
    display:flex; justify-content:space-between; align-items:center; }
.sug-item:hover, .sug-item.active { background:#e8eaf6; }
.sug-cat  { font-size:.72rem; color:#7986cb; background:#e8eaf6;
    padding:2px 7px; border-radius:10px; white-space:nowrap; }
</style>
@endpush

@section('content')
<div class="row justify-content-center">
<div class="col-lg-7">
<div class="card shadow-sm">
    <div class="card-header fw-bold" style="background:#1a237e;color:white">
        <i class="bi bi-box-seam"></i>
        {{ isset($producto) ? 'Editar: '.$producto->descripcion : 'Nuevo Producto' }}
    </div>
    <div class="card-body">

        @if($errors->any())
        <div class="alert alert-danger py-2">
            <ul class="mb-0 ps-3">@foreach($errors->all() as $e)<li>{{ $e }}</li>@endforeach</ul>
        </div>
        @endif

        <form action="{{ isset($producto) ? route('inventario.update',$producto->id) : route('inventario.store') }}"
              method="POST" id="frm-producto">
            @csrf
            @if(isset($producto)) @method('PUT') @endif

            <div class="row g-3">

                {{-- Descripción con autocompletado --}}
                <div class="col-12">
                    <label class="form-label fw-semibold">
                        Descripción *
                        @if(!isset($producto))
                        <small class="text-muted fw-normal ms-2">— escribe para buscar en la lista de productos</small>
                        @endif
                    </label>
                    <div class="position-relative">
                        <input type="text" name="descripcion" id="inp-desc" class="form-control"
                               value="{{ old('descripcion', $producto->descripcion ?? '') }}"
                               autocomplete="off" required
                               placeholder="Ej: Arroz 1 kg, Azúcar 1 kg...">
                        <div class="sug-box d-none" id="sug-box"></div>
                    </div>
                </div>

                {{-- Código y Categoría --}}
                <div class="col-6">
                    <label class="form-label fw-semibold">Código *</label>
                    <input type="text" name="codigo" id="inp-codigo" class="form-control"
                           value="{{ old('codigo', $producto->codigo ?? '') }}" required
                           placeholder="Ej: ALA001">
                </div>
                <div class="col-6">
                    <label class="form-label fw-semibold">Categoría</label>
                    <select name="categoria_id" id="sel-categoria" class="form-select">
                        <option value="">— Sin categoría —</option>
                        @foreach($categorias as $cat)
                        <option value="{{ $cat->id }}"
                            {{ old('categoria_id', $producto->categoria_id ?? '') == $cat->id ? 'selected' : '' }}>
                            {{ $cat->nombre }}
                        </option>
                        @endforeach
                    </select>
                </div>

                {{-- Precios --}}
                <div class="col-4">
                    <label class="form-label fw-semibold">Precio Compra $</label>
                    <input type="number" name="precio_compra" class="form-control text-end"
                           value="{{ old('precio_compra', $producto->precio_compra ?? '0') }}"
                           step="0.01" min="0" required>
                </div>
                <div class="col-4">
                    <label class="form-label fw-semibold">Precio Venta $ *</label>
                    <input type="number" name="precio_venta" class="form-control text-end"
                           value="{{ old('precio_venta', $producto->precio_venta ?? '0') }}"
                           step="0.01" min="0" required>
                </div>
                <div class="col-4">
                    <label class="form-label fw-semibold">Precio Mayorista $</label>
                    <input type="number" name="precio_mayorista" class="form-control text-end"
                           value="{{ old('precio_mayorista', $producto->precio_mayorista ?? '0') }}"
                           step="0.01" min="0" required>
                </div>

                {{-- Stock + IVA --}}
                <div class="col-4">
                    <label class="form-label fw-semibold">Stock actual</label>
                    <input type="number" name="stock" class="form-control text-center"
                           value="{{ old('stock', $producto->stock ?? '0') }}" min="0" required>
                </div>
                <div class="col-4">
                    <label class="form-label fw-semibold">Stock mínimo</label>
                    <input type="number" name="stock_minimo" class="form-control text-center"
                           value="{{ old('stock_minimo', $producto->stock_minimo ?? '5') }}" min="0" required>
                </div>
                <div class="col-4 d-flex align-items-end pb-1">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" name="tiene_iva" id="iva"
                               {{ old('tiene_iva', $producto->tiene_iva ?? true) ? 'checked' : '' }}>
                        <label class="form-check-label fw-semibold" for="iva">Tiene IVA (12%)</label>
                    </div>
                </div>
            </div>

            <div class="mt-4 d-flex gap-2">
                <button type="submit" class="btn btn-success px-4">
                    <i class="bi bi-save"></i> Guardar
                </button>
                <a href="{{ route('inventario.index') }}" class="btn btn-secondary">
                    <i class="bi bi-arrow-left"></i> Cancelar
                </a>
            </div>
        </form>
    </div>
</div>
</div></div>
@endsection

@push('scripts')
<script>
// prefijo por categoría
const CAT_PREFIX = {1:'ALA',2:'BEB',3:'LIM',4:'HIG',5:'SNA',6:'CON',7:'VAR'};

// ── Lista predefinida: nombre, categoría, IVA y precios sugeridos ─────────────
const PRODUCTOS_LISTA = [
  // Alimentos y Abarrotes
  { nombre:'Arroz 1 kg',           cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.60, pv:0.75, pm:0.68 },
  { nombre:'Azúcar 1 kg',          cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.60, pv:0.80, pm:0.70 },
  { nombre:'Sal 1 kg',             cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.25, pv:0.40, pm:0.35 },
  { nombre:'Harina 1 kg',          cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.70, pv:0.90, pm:0.82 },
  { nombre:'Fideos 400 g',         cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.55, pv:0.75, pm:0.68 },
  { nombre:'Aceite 1 L',           cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:2.00, pv:2.50, pm:2.30 },
  { nombre:'Leche 1 L',            cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.80, pv:1.00, pm:0.92 },
  { nombre:'Café 200 g',           cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:2.50, pv:3.20, pm:2.90 },
  { nombre:'Atún en lata',         cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:1.00, pv:1.40, pm:1.25 },
  { nombre:'Avena 500 g',          cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.90, pv:1.20, pm:1.08 },
  { nombre:'Pan de molde',         cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:1.00, pv:1.40, pm:1.25 },
  { nombre:'Pan integral',         cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:1.20, pv:1.60, pm:1.45 },
  { nombre:'Mayonesa',             cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:0.80, pv:1.10, pm:0.98 },
  { nombre:'Salsa de tomate',      cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:0.70, pv:0.95, pm:0.85 },
  { nombre:'Mostaza',              cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:0.75, pv:1.00, pm:0.90 },
  { nombre:'Vinagre',              cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.50, pv:0.70, pm:0.62 },
  { nombre:'Cubos de caldo',       cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:0.35, pv:0.50, pm:0.45 },
  { nombre:'Gelatina',             cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:0.40, pv:0.60, pm:0.52 },
  { nombre:'Mermelada',            cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:1.00, pv:1.40, pm:1.25 },
  { nombre:'Miel',                 cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:2.00, pv:2.80, pm:2.50 },
  { nombre:'Cereal para desayuno', cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:2.50, pv:3.50, pm:3.10 },
  { nombre:'Galletas rellenas',    cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:0.60, pv:0.85, pm:0.75 },
  { nombre:'Leche condensada',     cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:1.20, pv:1.60, pm:1.45 },
  { nombre:'Leche evaporada',      cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:1.00, pv:1.35, pm:1.22 },
  { nombre:'Maíz para canguil',    cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.60, pv:0.85, pm:0.75 },
  { nombre:'Canguil preparado',    cat_id:1, cat:'Alimentos y Abarrotes', iva:1, pc:0.50, pv:0.70, pm:0.62 },
  { nombre:'Banano 1 kg',          cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.30, pv:0.50, pm:0.45 },
  { nombre:'Manzana 1 kg',         cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:1.00, pv:1.50, pm:1.35 },
  { nombre:'Naranja 1 kg',         cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.40, pv:0.65, pm:0.55 },
  { nombre:'Tomate 1 kg',          cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.40, pv:0.65, pm:0.55 },
  { nombre:'Cebolla 1 kg',         cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.40, pv:0.65, pm:0.55 },
  { nombre:'Papa 1 kg',            cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.35, pv:0.55, pm:0.48 },
  { nombre:'Zanahoria 1 kg',       cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.30, pv:0.50, pm:0.45 },
  { nombre:'Lechuga',              cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.35, pv:0.55, pm:0.48 },
  { nombre:'Pepino',               cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.25, pv:0.40, pm:0.35 },
  { nombre:'Pimiento',             cat_id:1, cat:'Alimentos y Abarrotes', iva:0, pc:0.30, pv:0.50, pm:0.45 },
  // Bebidas
  { nombre:'Agua 600 ml',          cat_id:2, cat:'Bebidas', iva:0, pc:0.20, pv:0.35, pm:0.30 },
  { nombre:'Gaseosa 500 ml',       cat_id:2, cat:'Bebidas', iva:1, pc:0.40, pv:0.65, pm:0.55 },
  { nombre:'Jugo en caja',         cat_id:2, cat:'Bebidas', iva:1, pc:0.45, pv:0.70, pm:0.62 },
  { nombre:'Té frío',              cat_id:2, cat:'Bebidas', iva:1, pc:0.50, pv:0.75, pm:0.65 },
  { nombre:'Bebida energética',    cat_id:2, cat:'Bebidas', iva:1, pc:1.00, pv:1.50, pm:1.35 },
  { nombre:'Agua saborizada',      cat_id:2, cat:'Bebidas', iva:1, pc:0.45, pv:0.70, pm:0.60 },
  { nombre:'Leche chocolatada',    cat_id:2, cat:'Bebidas', iva:1, pc:0.55, pv:0.80, pm:0.70 },
  { nombre:'Yogur bebible',        cat_id:2, cat:'Bebidas', iva:1, pc:0.45, pv:0.70, pm:0.62 },
  { nombre:'Refresco 1 L',         cat_id:2, cat:'Bebidas', iva:1, pc:0.65, pv:1.00, pm:0.88 },
  { nombre:'Agua mineral',         cat_id:2, cat:'Bebidas', iva:0, pc:0.35, pv:0.55, pm:0.48 },
  // Snacks y Dulces
  { nombre:'Chocolate',            cat_id:5, cat:'Snacks y Dulces', iva:1, pc:0.60, pv:0.90, pm:0.80 },
  { nombre:'Caramelos',            cat_id:5, cat:'Snacks y Dulces', iva:1, pc:0.10, pv:0.20, pm:0.15 },
  { nombre:'Chicles',              cat_id:5, cat:'Snacks y Dulces', iva:1, pc:0.10, pv:0.20, pm:0.15 },
  { nombre:'Papas fritas',         cat_id:5, cat:'Snacks y Dulces', iva:1, pc:0.30, pv:0.50, pm:0.45 },
  { nombre:'Maní tostado',         cat_id:5, cat:'Snacks y Dulces', iva:1, pc:0.30, pv:0.50, pm:0.45 },
  { nombre:'Galletas dulces',      cat_id:5, cat:'Snacks y Dulces', iva:1, pc:0.40, pv:0.65, pm:0.55 },
  { nombre:'Galletas saladas',     cat_id:5, cat:'Snacks y Dulces', iva:1, pc:0.35, pv:0.55, pm:0.48 },
  { nombre:'Barra de cereal',      cat_id:5, cat:'Snacks y Dulces', iva:1, pc:0.50, pv:0.75, pm:0.65 },
  { nombre:'Helado pequeño',       cat_id:5, cat:'Snacks y Dulces', iva:1, pc:0.30, pv:0.50, pm:0.45 },
  { nombre:'Paleta de caramelo',   cat_id:5, cat:'Snacks y Dulces', iva:1, pc:0.15, pv:0.25, pm:0.22 },
  // Limpieza
  { nombre:'Detergente 500 g',     cat_id:3, cat:'Productos de Limpieza', iva:1, pc:1.20, pv:1.70, pm:1.50 },
  { nombre:'Cloro 1 L',            cat_id:3, cat:'Productos de Limpieza', iva:1, pc:0.80, pv:1.20, pm:1.05 },
  { nombre:'Desinfectante',        cat_id:3, cat:'Productos de Limpieza', iva:1, pc:1.50, pv:2.20, pm:1.95 },
  { nombre:'Jabón para ropa',      cat_id:3, cat:'Productos de Limpieza', iva:1, pc:0.50, pv:0.80, pm:0.70 },
  { nombre:'Esponja',              cat_id:3, cat:'Productos de Limpieza', iva:1, pc:0.30, pv:0.55, pm:0.48 },
  { nombre:'Lavavajillas',         cat_id:3, cat:'Productos de Limpieza', iva:1, pc:1.00, pv:1.50, pm:1.32 },
  { nombre:'Suavizante de ropa',   cat_id:3, cat:'Productos de Limpieza', iva:1, pc:1.50, pv:2.20, pm:1.95 },
  { nombre:'Limpiavidrios',        cat_id:3, cat:'Productos de Limpieza', iva:1, pc:1.50, pv:2.20, pm:1.95 },
  { nombre:'Escoba',               cat_id:3, cat:'Productos de Limpieza', iva:1, pc:2.50, pv:3.50, pm:3.10 },
  { nombre:'Trapeador',            cat_id:3, cat:'Productos de Limpieza', iva:1, pc:3.00, pv:4.50, pm:4.00 },
  // Higiene Personal
  { nombre:'Papel higiénico',      cat_id:4, cat:'Higiene Personal', iva:1, pc:1.00, pv:1.50, pm:1.32 },
  { nombre:'Pasta dental',         cat_id:4, cat:'Higiene Personal', iva:1, pc:1.00, pv:1.50, pm:1.32 },
  { nombre:'Cepillo dental',       cat_id:4, cat:'Higiene Personal', iva:1, pc:0.80, pv:1.20, pm:1.05 },
  { nombre:'Shampoo',              cat_id:4, cat:'Higiene Personal', iva:1, pc:2.50, pv:3.50, pm:3.10 },
  { nombre:'Jabón de baño',        cat_id:4, cat:'Higiene Personal', iva:1, pc:0.60, pv:0.90, pm:0.80 },
  { nombre:'Desodorante',          cat_id:4, cat:'Higiene Personal', iva:1, pc:2.00, pv:2.80, pm:2.50 },
  { nombre:'Toallas sanitarias',   cat_id:4, cat:'Higiene Personal', iva:1, pc:1.20, pv:1.80, pm:1.60 },
  { nombre:'Pañuelos desechables', cat_id:4, cat:'Higiene Personal', iva:1, pc:0.40, pv:0.65, pm:0.55 },
  { nombre:'Crema corporal',       cat_id:4, cat:'Higiene Personal', iva:1, pc:2.50, pv:3.50, pm:3.10 },
  { nombre:'Alcohol antiséptico',  cat_id:4, cat:'Higiene Personal', iva:1, pc:1.50, pv:2.20, pm:1.95 },
  // Congelados y Refrigerados
  { nombre:'Huevos (docena)',      cat_id:6, cat:'Congelados y Refrigerados', iva:0, pc:1.60, pv:2.00, pm:1.85 },
  { nombre:'Queso 500 g',          cat_id:6, cat:'Congelados y Refrigerados', iva:1, pc:2.50, pv:3.20, pm:2.85 },
  { nombre:'Mantequilla',          cat_id:6, cat:'Congelados y Refrigerados', iva:1, pc:1.50, pv:2.00, pm:1.80 },
  { nombre:'Yogur natural',        cat_id:6, cat:'Congelados y Refrigerados', iva:1, pc:1.00, pv:1.40, pm:1.25 },
  { nombre:'Jamón 250 g',          cat_id:6, cat:'Congelados y Refrigerados', iva:1, pc:2.20, pv:2.90, pm:2.60 },
  { nombre:'Salchichas',           cat_id:6, cat:'Congelados y Refrigerados', iva:1, pc:2.00, pv:2.70, pm:2.40 },
  { nombre:'Queso crema',          cat_id:6, cat:'Congelados y Refrigerados', iva:1, pc:1.80, pv:2.40, pm:2.15 },
  { nombre:'Margarina',            cat_id:6, cat:'Congelados y Refrigerados', iva:1, pc:0.90, pv:1.30, pm:1.15 },
  { nombre:'Leche deslactosada',   cat_id:6, cat:'Congelados y Refrigerados', iva:1, pc:1.20, pv:1.60, pm:1.42 },
  { nombre:'Yogur griego',         cat_id:6, cat:'Congelados y Refrigerados', iva:1, pc:1.50, pv:2.00, pm:1.80 },
  // Productos Varios
  { nombre:'Encendedor',           cat_id:7, cat:'Productos Varios', iva:1, pc:0.25, pv:0.50, pm:0.42 },
  { nombre:'Velas',                cat_id:7, cat:'Productos Varios', iva:1, pc:0.50, pv:0.80, pm:0.70 },
  { nombre:'Pilas AA',             cat_id:7, cat:'Productos Varios', iva:1, pc:0.50, pv:0.85, pm:0.75 },
  { nombre:'Pilas AAA',            cat_id:7, cat:'Productos Varios', iva:1, pc:0.50, pv:0.85, pm:0.75 },
  { nombre:'Cuadernos',            cat_id:7, cat:'Productos Varios', iva:1, pc:0.80, pv:1.25, pm:1.10 },
  { nombre:'Esferográficos',       cat_id:7, cat:'Productos Varios', iva:1, pc:0.15, pv:0.30, pm:0.25 },
  { nombre:'Lápices',              cat_id:7, cat:'Productos Varios', iva:1, pc:0.15, pv:0.30, pm:0.25 },
  { nombre:'Borradores',           cat_id:7, cat:'Productos Varios', iva:1, pc:0.10, pv:0.25, pm:0.20 },
  { nombre:'Sacapuntas',           cat_id:7, cat:'Productos Varios', iva:1, pc:0.15, pv:0.30, pm:0.25 },
  { nombre:'Fundas plásticas',     cat_id:7, cat:'Productos Varios', iva:1, pc:0.30, pv:0.50, pm:0.45 },
  { nombre:'Servilletas',          cat_id:7, cat:'Productos Varios', iva:1, pc:0.40, pv:0.65, pm:0.55 },
  { nombre:'Vasos desechables',    cat_id:7, cat:'Productos Varios', iva:1, pc:0.50, pv:0.80, pm:0.70 },
  { nombre:'Platos desechables',   cat_id:7, cat:'Productos Varios', iva:1, pc:0.60, pv:0.90, pm:0.80 },
  { nombre:'Fundas de basura',     cat_id:7, cat:'Productos Varios', iva:1, pc:0.80, pv:1.20, pm:1.05 },
];

// ── Autocompletado ────────────────────────────────────────────────────────────
const inpDesc   = document.getElementById('inp-desc');
const sugBox    = document.getElementById('sug-box');
const selCat    = document.getElementById('sel-categoria');
let   activeIdx = -1;

inpDesc.addEventListener('input', () => {
    const q = inpDesc.value.trim().toLowerCase();
    activeIdx = -1;
    if (!q) { sugBox.classList.add('d-none'); return; }

    const matches = PRODUCTOS_LISTA.filter(p =>
        p.nombre.toLowerCase().includes(q)
    ).slice(0, 20);

    if (!matches.length) { sugBox.classList.add('d-none'); return; }

    // guardamos índices en el array original para recuperar precios
    const matchesIdx = [];
    PRODUCTOS_LISTA.forEach((p, i) => { if (p.nombre.toLowerCase().includes(q)) matchesIdx.push(i); });
    const shown = matchesIdx.slice(0, 20);

    sugBox.innerHTML = shown.map(origIdx => {
        const p = PRODUCTOS_LISTA[origIdx];
        return `<div class="sug-item" data-orig="${origIdx}">
            <span>${resaltar(p.nombre, q)}</span>
            <span class="sug-cat">${p.cat}</span>
        </div>`;
    }).join('');

    sugBox.querySelectorAll('.sug-item').forEach(el => {
        el.addEventListener('mousedown', e => {
            e.preventDefault();
            seleccionar(el);
        });
    });
    sugBox.classList.remove('d-none');
});

inpDesc.addEventListener('keydown', e => {
    const items = sugBox.querySelectorAll('.sug-item');
    if (!items.length) return;
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIdx = Math.min(activeIdx + 1, items.length - 1);
        actualizarActivo(items);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIdx = Math.max(activeIdx - 1, 0);
        actualizarActivo(items);
    } else if (e.key === 'Enter' && activeIdx >= 0) {
        e.preventDefault();
        seleccionar(items[activeIdx]);
    } else if (e.key === 'Escape') {
        sugBox.classList.add('d-none');
    }
});

inpDesc.addEventListener('blur', () => {
    setTimeout(() => sugBox.classList.add('d-none'), 150);
});

function actualizarActivo(items) {
    items.forEach((el, i) => el.classList.toggle('active', i === activeIdx));
    if (activeIdx >= 0) items[activeIdx].scrollIntoView({ block:'nearest' });
}

function seleccionar(el) {
    const prod = PRODUCTOS_LISTA[parseInt(el.dataset.orig)];
    if (!prod) return;

    inpDesc.value = prod.nombre;
    if (selCat) selCat.value = prod.cat_id;

    const ivaCheck = document.getElementById('iva');
    if (ivaCheck) ivaCheck.checked = prod.iva === 1;

    document.querySelector('[name="precio_compra"]').value    = prod.pc.toFixed(2);
    document.querySelector('[name="precio_venta"]').value     = prod.pv.toFixed(2);
    document.querySelector('[name="precio_mayorista"]').value = prod.pm.toFixed(2);

    sugBox.classList.add('d-none');
    activeIdx = -1;

    // Stock y stock mínimo por defecto
    const inpStock    = document.querySelector('[name="stock"]');
    const inpStockMin = document.querySelector('[name="stock_minimo"]');
    inpStock.value    = 10;
    inpStockMin.value = 5;

    // Generar código automático desde el servidor
    const prefix = CAT_PREFIX[prod.cat_id] || 'PRD';
    const inp = document.getElementById('inp-codigo');
    inp.value    = '...';
    inp.disabled = true;
    fetch(`/api/productos/next-code?prefix=${prefix}`)
        .then(r => r.json())
        .then(data => {
            inp.value    = data.code;
            inp.disabled = false;
            // Enfocar stock para que solo escriban la cantidad
            inpStock.focus();
            inpStock.select();
        })
        .catch(() => { inp.value = prefix + '001'; inp.disabled = false; inpStock.focus(); });
}

function resaltar(texto, query) {
    const re = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')})`, 'gi');
    return texto.replace(re, '<strong>$1</strong>');
}
</script>
@endpush
