@extends('layouts.app')
@section('title','Facturación')
@push('styles')
<style>
/* ── layout ── */
#tbl-items thead th { font-size:.78rem; padding:5px 7px; }
#tbl-items tbody td { padding:4px 7px; vertical-align:middle; }
.totales-box .total-final { font-size:1.5rem; font-weight:800; color:#1b5e20; }
.autocomplete-list { position:absolute; z-index:1000; background:#fff;
    border:1px solid #dee2e6; border-radius:0 0 6px 6px;
    width:100%; max-height:200px; overflow-y:auto; }
.autocomplete-list .ac-item { padding:6px 12px; cursor:pointer; font-size:.82rem; }
.autocomplete-list .ac-item:hover { background:#e8eaf6; }
.cliente-badge { background:#e3f2fd; border-radius:6px; padding:4px 10px;
    display:inline-block; font-size:.82rem; }

@media print {
  body > *:not(.modal) { display:none !important; }
  .modal { position:static !important; display:block !important; }
  .modal-header.d-print-none { display:none !important; }
  .modal-dialog { max-width:100% !important; margin:0 !important; }
  .modal-content { border:none !important; box-shadow:none !important; }
}

/* ── categorías ── */
.cat-tabs { display:flex; flex-wrap:wrap; gap:4px; padding:8px; background:#f1f3f9;
    border-bottom:1px solid #dee2e6; }
.cat-btn { border:none; border-radius:20px; padding:4px 12px; font-size:.8rem;
    font-weight:600; cursor:pointer; background:#e8eaf6; color:#283593;
    transition:.15s; white-space:nowrap; }
.cat-btn.active, .cat-btn:hover { background:#283593; color:#fff; }

/* ── grilla de productos ── */
#prod-grid { display:grid;
    grid-template-columns: repeat(auto-fill, minmax(130px,1fr));
    gap:6px; padding:8px; max-height:240px; overflow-y:auto; }
.prod-card { border:1px solid #dee2e6; border-radius:8px; padding:8px 6px;
    text-align:center; cursor:pointer; background:#fff;
    transition:.15s; user-select:none; }
.prod-card:hover { background:#e8f5e9; border-color:#66bb6a; transform:scale(1.02); }
.prod-card:active { transform:scale(.97); }
.prod-card .pc-name { font-size:.75rem; font-weight:600; color:#1a237e;
    line-height:1.2; margin-bottom:3px; }
.prod-card .pc-price { font-size:.85rem; font-weight:800; color:#2e7d32; }
.prod-card .pc-stock { font-size:.68rem; color:#9e9e9e; }
.prod-card.sin-stock { opacity:.45; cursor:not-allowed; }
#prod-loading { text-align:center; padding:30px; color:#9e9e9e; }
</style>
@endpush

@section('content')
<div class="row g-2">

  {{-- ═══ IZQUIERDA: categorías + grilla + tabla de ítems ═══ --}}
  <div class="col-lg-8">

    {{-- Búsqueda rápida --}}
    <div class="card mb-2">
      <div class="card-body p-2">
        <div class="row g-2 position-relative">
          <div class="col-7 position-relative">
            <input type="text" id="inp-busqueda" class="form-control form-control-sm"
                   placeholder="🔍 Buscar producto por código o nombre...">
            <div class="autocomplete-list d-none" id="ac-list"></div>
          </div>
          <div class="col-2">
            <input type="number" id="inp-cantidad" class="form-control form-control-sm text-center"
                   value="1" min="1" placeholder="Cant">
          </div>
          <div class="col-3">
            <button class="btn btn-primary btn-sm w-100" onclick="agregarDesdeInput()">
              <i class="bi bi-plus-lg"></i> Agregar
            </button>
          </div>
        </div>
      </div>
    </div>

    {{-- Selector por categoría --}}
    <div class="card mb-2">
      <div class="cat-tabs" id="cat-tabs">
        @foreach($categorias as $cat)
        <button class="cat-btn" data-id="{{ $cat->id }}" onclick="cargarCategoria({{ $cat->id }}, this)">
          {{ $cat->nombre }}
        </button>
        @endforeach
      </div>
      <div id="prod-grid">
        <div id="prod-loading" style="grid-column:1/-1">
          <i class="bi bi-grid text-muted" style="font-size:2rem"></i><br>
          <small>Selecciona una categoría</small>
        </div>
      </div>
    </div>

    {{-- Tabla de ítems del comprobante --}}
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center py-2">
        <span><i class="bi bi-receipt"></i> Detalle del Comprobante
          <span class="badge bg-warning text-dark ms-2" id="lbl-numero">{{ $numero }}</span>
        </span>
        <span class="fw-bold me-2" style="color:#FF6F00;font-size:.85rem;font-family:monospace">
          <i class="bi bi-clock-fill"></i> <span id="lbl-fecha-hora">--/--/---- --:--:--</span>
        </span>
        <button class="btn btn-outline-danger btn-sm" onclick="borrarTodo()">
          <i class="bi bi-trash"></i> Limpiar
        </button>
      </div>
      <div class="card-body p-0">
        <div style="max-height:220px;overflow-y:auto">
          <table class="table table-sm table-bordered mb-0" id="tbl-items">
            <thead class="table-dark">
              <tr>
                <th style="width:28px">#</th>
                <th style="width:28px">IVA</th>
                <th style="width:55px">Cant</th>
                <th style="width:90px">Código</th>
                <th>Descripción</th>
                <th style="width:80px" class="text-end">V.Unit</th>
                <th style="width:85px" class="text-end">Subtotal</th>
                <th style="width:32px"></th>
              </tr>
            </thead>
            <tbody id="tbody-items">
              <tr id="tr-empty"><td colspan="8" class="text-center text-muted py-3">
                <i class="bi bi-cart"></i> Sin productos — selecciona de la grilla o busca arriba
              </td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>

  {{-- ═══ DERECHA: totales, pago, cliente, emitir ═══ --}}
  <div class="col-lg-4">

    {{-- Totales --}}
    <div class="card mb-2">
      <div class="card-header py-2"><i class="bi bi-calculator"></i> Totales</div>
      <div class="card-body p-3 totales-box">
        <div class="d-flex justify-content-between mb-1">
          <span>Subtotal:</span><strong id="lbl-subtotal">$ 0.00</strong>
        </div>
        <div class="d-flex justify-content-between mb-1">
          <span>IVA 15%:</span><strong id="lbl-iva">$ 0.00</strong>
        </div>
        <div class="d-flex justify-content-between mb-1">
          <span>Descuento:</span>
          <div class="input-group input-group-sm" style="width:100px">
            <span class="input-group-text">$</span>
            <input type="number" id="inp-descuento" class="form-control text-end"
                   value="0" min="0" step="0.01" oninput="calcularTotales()">
          </div>
        </div>
        <hr class="my-2">
        <div class="d-flex justify-content-between">
          <span class="fw-bold fs-5">TOTAL:</span>
          <span class="total-final" id="lbl-total">$ 0.00</span>
        </div>
      </div>
    </div>

    {{-- Forma de pago --}}
    <div class="card mb-2">
      <div class="card-header py-2"><i class="bi bi-credit-card"></i> Forma de Pago</div>
      <div class="card-body p-2">
        @foreach(['Efectivo','Tarjeta de Crédito','Tarjeta de Débito','Transferencia Bancaria','Dinero Electrónico'] as $fp)
        <div class="d-flex align-items-center mb-1 gap-2">
          <input class="form-check-input mt-0" type="checkbox" id="fp-{{ $loop->index }}"
                 value="{{ $fp }}" {{ $fp==='Efectivo' ? 'checked' : '' }} onchange="actualizarPago()">
          <label class="form-check-label flex-grow-1 small" for="fp-{{ $loop->index }}">{{ $fp }}</label>
          <input type="number" class="form-control form-control-sm text-end fp-monto"
                 style="width:78px" placeholder="0.00" min="0" step="0.01"
                 data-fp="{{ $fp }}" {{ $fp!=='Efectivo' ? 'disabled' : '' }}>
        </div>
        @endforeach
      </div>
    </div>

    {{-- Cliente --}}
    <div class="card mb-2">
      <div class="card-header py-2"><i class="bi bi-person"></i> Cliente</div>
      <div class="card-body p-2">
        <div class="d-flex gap-2 mb-2">
          <input type="text" id="inp-cedula" class="form-control form-control-sm"
                 placeholder="Ingrese cédula o RUC..."
                 onkeydown="if(event.key==='Enter')buscarCliente()"
                 oninput="buscarClienteAuto()">
          <button class="btn btn-sm btn-primary" onclick="buscarCliente()" title="Buscar cliente">
            <i class="bi bi-search"></i>
          </button>
          <button class="btn btn-sm btn-outline-secondary" onclick="clienteFinal()" title="Consumidor Final">CF</button>
          <button class="btn btn-sm btn-outline-success" title="Registrar nuevo cliente" onclick="abrirModalCliente()">
            <i class="bi bi-person-plus"></i>
          </button>
        </div>
        {{-- Datos del cliente encontrado --}}
        <div id="box-cliente" class="rounded p-2" style="background:#f8f9fa;border:1px solid #dee2e6;min-height:52px">
          <div class="d-flex align-items-center gap-2">
            <i class="bi bi-person-circle fs-4 text-secondary" id="ico-cliente"></i>
            <div>
              <div class="fw-bold" id="lbl-cliente-nombre">CONSUMIDOR FINAL</div>
              <small class="text-muted" id="lbl-cliente-info">9999999999</small>
            </div>
          </div>
        </div>
        <input type="hidden" id="hid-cliente-id" value="{{ $consumidor->id ?? '' }}">
      </div>
    </div>

    {{-- Tipo + Emitir --}}
    <div class="card">
      <div class="card-body p-3">
        <div class="d-flex gap-3 mb-3">
          <div class="form-check">
            <input class="form-check-input" type="radio" name="tipo" id="tipo-factura" value="factura" checked>
            <label class="form-check-label" for="tipo-factura">Factura</label>
          </div>
          <div class="form-check">
            <input class="form-check-input" type="radio" name="tipo" id="tipo-recibo" value="recibo">
            <label class="form-check-label" for="tipo-recibo">Recibo</label>
          </div>
        </div>
        <button class="btn btn-success w-100 py-2 fw-bold" onclick="emitirFactura()">
          <i class="bi bi-printer"></i> EMITIR FACTURA
        </button>
        <div class="d-flex gap-2 mt-2">
          <button class="btn btn-outline-danger btn-sm flex-fill" onclick="borrarTodo()">
            <i class="bi bi-trash"></i> Borrar
          </button>
          <button class="btn btn-outline-secondary btn-sm flex-fill"
                  data-bs-toggle="modal" data-bs-target="#modalAnular">
            <i class="bi bi-x-circle"></i> Anular
          </button>
        </div>
      </div>
    </div>

  </div>
</div>

{{-- Modal Anular --}}
<div class="modal fade" id="modalAnular" tabindex="-1">
  <div class="modal-dialog modal-sm">
    <div class="modal-content">
      <div class="modal-header">
        <h6 class="modal-title">Anular Factura</h6>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <input type="text" id="inp-anular" class="form-control" placeholder="N° de factura">
      </div>
      <div class="modal-footer">
        <button class="btn btn-danger btn-sm" onclick="anularFactura()">Anular</button>
        <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancelar</button>
      </div>
    </div>
  </div>
</div>

{{-- Toast --}}
<div class="position-fixed bottom-0 end-0 p-3" style="z-index:9999">
  <div id="toast-msg" class="toast align-items-center text-white border-0" role="alert">
    <div class="d-flex">
      <div class="toast-body" id="toast-body"></div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  </div>
</div>

{{-- Modal Factura Emitida --}}
<div class="modal fade" id="modalFactura" tabindex="-1" data-bs-backdrop="static">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header py-2 d-print-none" style="background:#2D2D2D">
        <h6 class="modal-title text-white"><i class="bi bi-receipt"></i> Factura Emitida</h6>
        <div class="ms-auto d-flex gap-2">
          <button class="btn btn-sm btn-warning" onclick="window.print()"><i class="bi bi-printer"></i> Imprimir</button>
          <button class="btn btn-sm btn-outline-light" data-bs-dismiss="modal">Cerrar</button>
        </div>
      </div>
      <div class="modal-body p-4" id="contenido-factura">
        {{-- Se llena dinámicamente --}}
      </div>
    </div>
  </div>
</div>

{{-- Modal Nuevo Cliente --}}
<div class="modal fade" id="modalNuevoCliente" tabindex="-1">
  <div class="modal-dialog modal-md">
    <div class="modal-content">
      <div class="modal-header py-2" style="background:#2D2D2D">
        <h6 class="modal-title text-white"><i class="bi bi-person-plus"></i> Registrar Nuevo Cliente</h6>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body p-3">
        <div id="modal-cli-error" class="alert alert-danger py-2 d-none"></div>
        <div class="row g-2">
          <div class="col-8">
            <label class="form-label fw-semibold small">Cédula / RUC <span class="text-danger">*</span></label>
            <input type="text" id="mc-cedula" class="form-control form-control-sm"
                   placeholder="10 dígitos (natural) o 13 (RUC)" maxlength="13"
                   oninput="mcDetectarTipo(this.value)">
            <div id="mc-cedula-fb" class="form-text"></div>
          </div>
          <div class="col-4">
            <label class="form-label fw-semibold small">Tipo <span class="text-danger">*</span></label>
            <select id="mc-tipo" class="form-select form-select-sm">
              <option value="natural">Persona Natural</option>
              <option value="juridico">Persona Jurídica</option>
            </select>
          </div>
          <div class="col-6">
            <label class="form-label fw-semibold small">Nombre <span class="text-danger">*</span></label>
            <input type="text" id="mc-nombre" class="form-control form-control-sm" placeholder="Nombre(s)">
          </div>
          <div class="col-6">
            <label class="form-label small">Apellido</label>
            <input type="text" id="mc-apellido" class="form-control form-control-sm" placeholder="Apellido(s)">
          </div>
          <div class="col-12">
            <label class="form-label small">Dirección</label>
            <input type="text" id="mc-direccion" class="form-control form-control-sm" placeholder="Calle, número...">
          </div>
          <div class="col-6">
            <label class="form-label small">Teléfono</label>
            <input type="text" id="mc-telefono" class="form-control form-control-sm" placeholder="09XXXXXXXX">
          </div>
          <div class="col-6">
            <label class="form-label small">Email</label>
            <input type="email" id="mc-email" class="form-control form-control-sm" placeholder="correo@ejemplo.com">
          </div>
        </div>
      </div>
      <div class="modal-footer py-2">
        <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancelar</button>
        <button type="button" class="btn btn-success btn-sm" onclick="guardarNuevoCliente()">
          <i class="bi bi-save"></i> Guardar Cliente
        </button>
      </div>
    </div>
  </div>
</div>
@endsection

@push('scripts')
<script>
// Forzar recarga limpia si el navegador tiene JS viejo en caché
(function(){
  const V = 'tutifv5';
  if(localStorage.getItem('factura_js_v') !== V){
    localStorage.setItem('factura_js_v', V);
    location.replace('/facturacion?_=' + Date.now());
    return;
  }
  if(location.search) history.replaceState(null,'','/facturacion');
})();

const IVA = 15;
let items = [], acResults = [];

// ── CATEGORÍAS ───────────────────────────────────────────────────────────────
async function cargarCategoria(id, btn) {
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  const grid = document.getElementById('prod-grid');
  grid.innerHTML = '<div id="prod-loading" style="grid-column:1/-1;text-align:center;padding:20px"><div class="spinner-border spinner-border-sm text-primary"></div></div>';
  const res  = await fetch(`/api/productos/categoria?cat=${id}`);
  const data = await res.json();
  if (!data.length) {
    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:20px;color:#9e9e9e">Sin productos en esta categoría</div>';
    return;
  }
  grid.innerHTML = data.map(p => `
    <div class="prod-card ${p.stock <= 0 ? 'sin-stock' : ''}"
         onclick="${p.stock > 0 ? `addItem(${JSON.stringify(p).replace(/"/g,"'")})` : 'showToast(\"Sin stock\",\"warning\")'}"
         title="${p.descripcion} — Stock: ${p.stock}">
      <div class="pc-name">${p.descripcion}</div>
      <div class="pc-price">$${parseFloat(p.precio_venta).toFixed(2)}</div>
      <div class="pc-stock">Stock: ${p.stock}</div>
    </div>`).join('');
}

// ── AUTOCOMPLETE ─────────────────────────────────────────────────────────────
const inp   = document.getElementById('inp-busqueda');
const acList = document.getElementById('ac-list');

inp.addEventListener('input', async () => {
  const q = inp.value.trim();
  if (q.length < 1) { acList.classList.add('d-none'); return; }
  const res = await fetch(`/api/productos/buscar?q=${encodeURIComponent(q)}`);
  acResults = await res.json();
  acList.innerHTML = '';
  if (!acResults.length) { acList.classList.add('d-none'); return; }
  acResults.forEach(p => {
    const div = document.createElement('div');
    div.className = 'ac-item';
    div.innerHTML = `<strong>${p.codigo}</strong> — ${p.descripcion} <span class="text-success float-end">$${parseFloat(p.precio_venta).toFixed(2)}</span>`;
    div.onclick = () => { addItem(p); acList.classList.add('d-none'); inp.value = ''; };
    acList.appendChild(div);
  });
  acList.classList.remove('d-none');
});
inp.addEventListener('keydown', e => {
  if (e.key === 'Enter') { agregarDesdeInput(); e.preventDefault(); }
  if (e.key === 'Escape') acList.classList.add('d-none');
});
document.addEventListener('click', e => { if (!inp.contains(e.target)) acList.classList.add('d-none'); });

function agregarDesdeInput() {
  if (acResults.length === 1) { addItem(acResults[0]); inp.value = ''; acList.classList.add('d-none'); return; }
  const exact = acResults.find(p => p.codigo === inp.value.trim());
  if (exact) { addItem(exact); inp.value = ''; acList.classList.add('d-none'); }
  else if (acResults.length) acList.classList.remove('d-none');
}

// ── ITEMS ────────────────────────────────────────────────────────────────────
function addItem(prod) {
  const cant = parseInt(document.getElementById('inp-cantidad').value) || 1;
  document.getElementById('inp-cantidad').value = 1;
  const idx = items.findIndex(i => i.producto_id === prod.id);
  if (idx >= 0) {
    items[idx].cantidad += cant;
    items[idx].subtotal  = items[idx].precio_unitario * items[idx].cantidad;
  } else {
    items.push({
      producto_id:    prod.id,
      codigo:         prod.codigo,
      descripcion:    prod.descripcion,
      precio_unitario: parseFloat(prod.precio_venta),
      tiene_iva:      prod.tiene_iva,
      cantidad:       cant,
      subtotal:       parseFloat(prod.precio_venta) * cant
    });
  }
  renderTable();
  calcularTotales();
  showToast(`✓ ${prod.descripcion} agregado`, 'success');
}

function renderTable() {
  const tbody = document.getElementById('tbody-items');
  if (!items.length) {
    tbody.innerHTML = '<tr id="tr-empty"><td colspan="8" class="text-center text-muted py-3"><i class="bi bi-cart"></i> Sin productos — selecciona de la grilla o busca arriba</td></tr>';
    return;
  }
  tbody.innerHTML = items.map((it, i) => `
    <tr>
      <td class="text-center">${i+1}</td>
      <td class="text-center">${it.tiene_iva ? '<span class="badge bg-info text-dark" style="font-size:.65rem">IVA</span>':''}</td>
      <td><input type="number" class="form-control form-control-sm text-center p-0"
                 style="width:48px" value="${it.cantidad}" min="1"
                 onchange="cambiarCant(${i},this.value)"></td>
      <td class="text-muted" style="font-size:.73rem">${it.codigo}</td>
      <td style="font-size:.83rem">${it.descripcion}</td>
      <td class="text-end">$${it.precio_unitario.toFixed(2)}</td>
      <td class="text-end fw-semibold text-success">$${it.subtotal.toFixed(2)}</td>
      <td class="text-center">
        <button class="btn btn-outline-danger btn-sm py-0 px-1" onclick="removeItem(${i})">
          <i class="bi bi-x"></i>
        </button>
      </td>
    </tr>`).join('');
}

function cambiarCant(i,v){ items[i].cantidad=parseInt(v)||1; items[i].subtotal=items[i].precio_unitario*items[i].cantidad; renderTable(); calcularTotales(); }
function removeItem(i){ items.splice(i,1); renderTable(); calcularTotales(); }
function resetFactura(){ items=[]; renderTable(); calcularTotales(); clienteFinal(); document.getElementById('inp-descuento').value=0; }
function borrarTodo(){ if(!items.length||confirm('¿Borrar todos los ítems?')){ resetFactura(); } }

// ── TOTALES ──────────────────────────────────────────────────────────────────
function calcularTotales(){
  let sub=0, iva=0;
  items.forEach(it=>{
    if(it.tiene_iva){ const base=it.subtotal/(1+IVA/100); sub+=base; iva+=it.subtotal-base; }
    else { sub+=it.subtotal; }
  });
  const desc=parseFloat(document.getElementById('inp-descuento').value)||0;
  const total=sub+iva-desc;
  document.getElementById('lbl-subtotal').textContent=`$ ${sub.toFixed(2)}`;
  document.getElementById('lbl-iva').textContent=`$ ${iva.toFixed(2)}`;
  document.getElementById('lbl-total').textContent=`$ ${Math.max(0,total).toFixed(2)}`;
  const ef=document.querySelector('[data-fp="Efectivo"]');
  if(ef&&document.getElementById('fp-0').checked) ef.value=Math.max(0,total).toFixed(2);
}

function actualizarPago(){
  document.querySelectorAll('.fp-monto').forEach((inp,i)=>{
    const cb=document.getElementById(`fp-${i}`);
    inp.disabled=!cb?.checked; if(!cb?.checked) inp.value='';
  });
  calcularTotales();
}

// ── CLIENTE ──────────────────────────────────────────────────────────────────
async function buscarCliente(){
  const q=document.getElementById('inp-cedula').value.trim(); if(!q) return;
  const res=await fetch(`/api/clientes/buscar?q=${encodeURIComponent(q)}`);
  const data=await res.json();
  if(data.length) setCliente(data[0]);
  else setClienteNoEncontrado(q);
}
async function buscarClienteAuto(){
  const q=document.getElementById('inp-cedula').value.trim();
  if(q.length<10) { resetClienteBox(); return; }
  const res=await fetch(`/api/clientes/buscar?q=${encodeURIComponent(q)}`);
  const data=await res.json();
  if(data.length) setCliente(data[0]);
  else setClienteNoEncontrado(q);
}
function setCliente(c){
  document.getElementById('hid-cliente-id').value=c.id;
  document.getElementById('lbl-cliente-nombre').textContent=c.nombre+(c.apellido?' '+c.apellido:'');
  const info=[];
  if(c.cedula) info.push('CI: '+c.cedula);
  if(c.telefono) info.push('📞 '+c.telefono);
  document.getElementById('lbl-cliente-info').textContent=info.join('  |  ');
  const box=document.getElementById('box-cliente');
  box.style.background='#e8f5e9'; box.style.borderColor='#66bb6a';
  document.getElementById('ico-cliente').className='bi bi-person-check-fill fs-4 text-success';
}
function setClienteNoEncontrado(cedula){
  // Factura como consumidor final pero avisa que no está registrado
  document.getElementById('hid-cliente-id').value='{{ $consumidor->id ?? "" }}';
  document.getElementById('lbl-cliente-nombre').textContent='CONSUMIDOR FINAL';
  document.getElementById('lbl-cliente-info').textContent='Cédula '+cedula+' no registrada — regístrela en ➕';
  const box=document.getElementById('box-cliente');
  box.style.background='#fff8e1'; box.style.borderColor='#ffb300';
  document.getElementById('ico-cliente').className='bi bi-person-exclamation fs-4 text-warning';
}
function resetClienteBox(){
  if(document.getElementById('inp-cedula').value.trim()==='') clienteFinal();
}
function clienteFinal(){
  document.getElementById('hid-cliente-id').value='{{ $consumidor->id ?? "" }}';
  document.getElementById('lbl-cliente-nombre').textContent='CONSUMIDOR FINAL';
  document.getElementById('lbl-cliente-info').textContent='9999999999';
  document.getElementById('inp-cedula').value='';
  const box=document.getElementById('box-cliente');
  box.style.background='#f8f9fa'; box.style.borderColor='#dee2e6';
  document.getElementById('ico-cliente').className='bi bi-person-circle fs-4 text-secondary';
}

// ── EMITIR ───────────────────────────────────────────────────────────────────
async function emitirFactura(){
  if(!items.length){ showToast('Agregue productos primero.','warning'); return; }
  const clienteId=document.getElementById('hid-cliente-id').value;
  if(!clienteId){ showToast('Seleccione un cliente.','warning'); return; }
  const formasPago=[...document.querySelectorAll('.fp-monto')]
    .filter((_,i)=>document.getElementById(`fp-${i}`)?.checked)
    .map(inp=>inp.dataset.fp).join(', ');
  if(!formasPago){ showToast('Seleccione forma de pago.','warning'); return; }
  const tipo=document.querySelector('input[name="tipo"]:checked').value;
  const descuento=parseFloat(document.getElementById('inp-descuento').value)||0;
  const payload={
    items:items.map(it=>({producto_id:it.producto_id,cantidad:it.cantidad})),
    cliente_id:parseInt(clienteId), forma_pago:formasPago,
    tipo_comprobante:tipo, descuento:descuento,
    _token:document.querySelector('meta[name="csrf-token"]').content
  };
  const res=await fetch('/facturacion/emitir',{
    method:'POST',
    headers:{'Content-Type':'application/json','X-CSRF-TOKEN':payload._token},
    body:JSON.stringify(payload)
  });
  const data=await res.json();
  if(data.success){
    resetFactura();
    document.getElementById('lbl-numero').textContent=data.numero;
    mostrarFacturaModal(data);
  } else {
    showToast('Error: '+(data.error||'Intente de nuevo'),'danger');
  }
}

function mostrarFacturaModal(d){
  const filas = d.items.map(it=>`
    <tr>
      <td>${it.descripcion}${it.tiene_iva?'<span class="badge ms-1" style="background:#e3f2fd;color:#1565c0;font-size:.65rem">IVA</span>':''}</td>
      <td class="text-center">${it.cantidad}</td>
      <td class="text-end">$${it.precio_unitario}</td>
      <td class="text-end fw-semibold">$${it.subtotal}</td>
    </tr>`).join('');

  document.getElementById('contenido-factura').innerHTML=`
    <div style="font-family:Arial,sans-serif">
      <!-- Encabezado -->
      <div class="text-center py-3 mb-3 rounded" style="background:#2D2D2D;color:#fff">
        <div style="font-size:1.4rem;font-weight:800;color:#FF6F00">🍓 TUTI FRUT</div>
        <small>RUC: 1713175071001 &nbsp;|&nbsp; Sistema de Facturación</small>
      </div>

      <!-- Número y tipo -->
      <div class="d-flex justify-content-between align-items-center mb-3">
        <div>
          <span class="badge fs-6" style="background:#FF6F00">${d.tipo} N° ${d.numero}</span>
        </div>
        <div class="text-end">
          <div class="fw-bold">${d.fecha}</div>
          <small class="text-muted">F. de Pago: ${d.forma_pago}</small>
        </div>
      </div>

      <!-- Cliente y cajero -->
      <div class="row mb-3 g-2">
        <div class="col-6 p-2 rounded" style="background:#f8f9fa;border:1px solid #dee2e6">
          <div class="text-muted small fw-bold mb-1">CLIENTE</div>
          <div class="fw-bold">${d.cliente.nombre||'CONSUMIDOR FINAL'}</div>
          <small>CI/RUC: ${d.cliente.cedula||'9999999999'}</small>
          ${d.cliente.telefono?`<br><small>📞 ${d.cliente.telefono}</small>`:''}
        </div>
        <div class="col-6 p-2 rounded" style="background:#f8f9fa;border:1px solid #dee2e6">
          <div class="text-muted small fw-bold mb-1">ATENDIDO POR</div>
          <div class="fw-bold" style="color:#FF6F00">${d.cajero}</div>
        </div>
      </div>

      <!-- Productos -->
      <table class="table table-sm table-bordered mb-3">
        <thead style="background:#2D2D2D;color:#fff">
          <tr><th>Descripción</th><th class="text-center">Cant</th><th class="text-end">P.Unit</th><th class="text-end">Total</th></tr>
        </thead>
        <tbody>${filas}</tbody>
      </table>

      <!-- Totales -->
      <div class="row justify-content-end">
        <div class="col-5">
          <table class="table table-sm mb-0">
            <tr><td>Subtotal:</td><td class="text-end">$${d.subtotal}</td></tr>
            <tr><td>IVA 15%:</td><td class="text-end">$${d.iva}</td></tr>
            ${parseFloat(d.descuento)>0?`<tr><td>Descuento:</td><td class="text-end text-danger">-$${d.descuento}</td></tr>`:''}
            <tr style="background:#e8f5e9;font-weight:bold;font-size:1.1rem">
              <td>TOTAL:</td><td class="text-end">$${d.total}</td>
            </tr>
          </table>
        </div>
      </div>

      <div class="text-center mt-3 text-muted small">¡Gracias por su compra en TUTI FRUT!</div>
    </div>`;

  new bootstrap.Modal(document.getElementById('modalFactura')).show();
}

async function anularFactura(){
  const numero=document.getElementById('inp-anular').value.trim(); if(!numero) return;
  const res=await fetch('/facturacion/anular',{
    method:'POST',
    headers:{'Content-Type':'application/json',
             'X-CSRF-TOKEN':document.querySelector('meta[name="csrf-token"]').content},
    body:JSON.stringify({numero})
  });
  const data=await res.json();
  bootstrap.Modal.getInstance(document.getElementById('modalAnular')).hide();
  showToast(data.success?`Factura ${numero} anulada.`:data.error, data.success?'success':'danger');
}

function showToast(msg,type='success'){
  const el=document.getElementById('toast-msg');
  el.className=`toast align-items-center text-white border-0 bg-${type}`;
  document.getElementById('toast-body').textContent=msg;
  new bootstrap.Toast(el,{delay:3000}).show();
}

// ── MODAL NUEVO CLIENTE ──────────────────────────────────────────────────────
function abrirModalCliente(){
  // Pre-llenar cédula si ya escribió una
  const ced = document.getElementById('inp-cedula').value.trim();
  if(ced) { document.getElementById('mc-cedula').value=ced; mcDetectarTipo(ced); }
  document.getElementById('modal-cli-error').classList.add('d-none');
  new bootstrap.Modal(document.getElementById('modalNuevoCliente')).show();
}
function mcDetectarTipo(val){
  const fb=document.getElementById('mc-cedula-fb');
  const sel=document.getElementById('mc-tipo');
  if(val.length===10){ sel.value='natural'; fb.innerHTML='<span class="text-success">Cédula — Persona Natural</span>'; }
  else if(val.length===13){ sel.value='juridico'; fb.innerHTML='<span class="text-primary">RUC — Persona Jurídica</span>'; }
  else { fb.textContent=val.length+'/10'; }
}
async function guardarNuevoCliente(){
  const cedula  = document.getElementById('mc-cedula').value.trim();
  const nombre  = document.getElementById('mc-nombre').value.trim();
  const apellido= document.getElementById('mc-apellido').value.trim();
  const tipo    = document.getElementById('mc-tipo').value;
  const telefono= document.getElementById('mc-telefono').value.trim();
  const email   = document.getElementById('mc-email').value.trim();
  const direccion=document.getElementById('mc-direccion').value.trim();
  const errDiv  = document.getElementById('modal-cli-error');

  if(!cedula||!nombre){ errDiv.textContent='Cédula y Nombre son obligatorios.'; errDiv.classList.remove('d-none'); return; }

  const res = await fetch('{{ route("clientes.store") }}', {
    method:'POST',
    headers:{'Content-Type':'application/json','X-CSRF-TOKEN':'{{ csrf_token() }}','Accept':'application/json'},
    body: JSON.stringify({cedula,nombre,apellido,direccion,telefono,email,tipo})
  });
  const data = await res.json();
  if(data.ok){
    bootstrap.Modal.getInstance(document.getElementById('modalNuevoCliente')).hide();
    setCliente(data.cliente);
    document.getElementById('inp-cedula').value=data.cliente.cedula;
    showToast('Cliente registrado correctamente','success');
    // Limpiar campos del modal
    ['mc-cedula','mc-nombre','mc-apellido','mc-telefono','mc-email','mc-direccion'].forEach(id=>document.getElementById(id).value='');
  } else {
    const msg = data.errors ? Object.values(data.errors).flat().join(' | ') : 'Error al guardar.';
    errDiv.textContent=msg; errDiv.classList.remove('d-none');
  }
}

// Reloj en tiempo real (hora local del navegador)
function actualizarReloj(){
  const now = new Date();
  const p = n => String(n).padStart(2,'0');
  const texto = `${p(now.getDate())}/${p(now.getMonth()+1)}/${now.getFullYear()}  ${p(now.getHours())}:${p(now.getMinutes())}:${p(now.getSeconds())}`;
  const el = document.getElementById('lbl-fecha-hora');
  if(el) el.textContent = texto;
}
actualizarReloj();
setInterval(actualizarReloj, 1000);

// Cargar primera categoría al abrir
window.addEventListener('DOMContentLoaded', () => {
  actualizarReloj();
  const firstBtn = document.querySelector('.cat-btn');
  if (firstBtn) firstBtn.click();
});
</script>
@endpush
