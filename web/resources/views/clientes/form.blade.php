@extends('layouts.app')
@section('title', isset($cliente) ? 'Editar Cliente' : 'Nuevo Cliente')
@section('content')
<div class="row justify-content-center">
<div class="col-lg-6">
<div class="card">
    <div class="card-header">
        <i class="bi bi-person"></i>
        {{ isset($cliente) ? 'Editar: '.$cliente->nombre_completo : 'Nuevo Cliente' }}
    </div>
    <div class="card-body">
        @if($errors->any())
        <div class="alert alert-danger py-2">
            <ul class="mb-0 ps-3">@foreach($errors->all() as $e)<li>{{ $e }}</li>@endforeach</ul>
        </div>
        @endif

        <form action="{{ isset($cliente) ? route('clientes.update',$cliente->id) : route('clientes.store') }}"
              method="POST">
            @csrf
            @if(isset($cliente)) @method('PUT') @endif

            <div class="row g-3">
                {{-- Cédula con detección automática --}}
                <div class="col-8">
                    <label class="form-label fw-semibold">Cédula / RUC <span class="text-danger">*</span></label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-fingerprint"></i></span>
                        <input type="text" name="cedula" id="inp-cedula" class="form-control"
                               value="{{ old('cedula',$cliente->cedula ?? '') }}"
                               placeholder="10 dígitos (natural) o 13 (RUC)"
                               maxlength="13" required
                               oninput="detectarTipoCedula(this.value)">
                    </div>
                    <div id="cedula-feedback" class="form-text"></div>
                </div>
                <div class="col-4">
                    <label class="form-label fw-semibold">Tipo <span class="text-danger">*</span></label>
                    <select name="tipo" id="sel-tipo" class="form-select">
                        <option value="natural"  {{ old('tipo',$cliente->tipo ?? 'natural') === 'natural'  ? 'selected':'' }}>Persona Natural</option>
                        <option value="juridico" {{ old('tipo',$cliente->tipo ?? '') === 'juridico' ? 'selected':'' }}>Persona Jurídica</option>
                    </select>
                </div>

                <div class="col-6">
                    <label class="form-label fw-semibold">Nombre <span class="text-danger">*</span></label>
                    <input type="text" name="nombre" id="inp-nombre" class="form-control"
                           value="{{ old('nombre',$cliente->nombre ?? '') }}" required
                           placeholder="Nombre(s)">
                </div>
                <div class="col-6">
                    <label class="form-label fw-semibold">Apellido</label>
                    <input type="text" name="apellido" id="inp-apellido" class="form-control"
                           value="{{ old('apellido',$cliente->apellido ?? '') }}"
                           placeholder="Apellido(s)">
                </div>
                <div class="col-12">
                    <label class="form-label">Dirección</label>
                    <input type="text" name="direccion" class="form-control"
                           value="{{ old('direccion',$cliente->direccion ?? '') }}"
                           placeholder="Calle, número, sector...">
                </div>
                <div class="col-6">
                    <label class="form-label">Teléfono</label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-phone"></i></span>
                        <input type="text" name="telefono" class="form-control"
                               value="{{ old('telefono',$cliente->telefono ?? '') }}"
                               placeholder="09XXXXXXXX">
                    </div>
                </div>
                <div class="col-6">
                    <label class="form-label">Email</label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                        <input type="email" name="email" class="form-control"
                               value="{{ old('email',$cliente->email ?? '') }}"
                               placeholder="correo@ejemplo.com">
                    </div>
                </div>
            </div>

            <div class="mt-4 d-flex gap-2">
                <button type="submit" class="btn btn-success">
                    <i class="bi bi-save"></i> Guardar Cliente
                </button>
                <a href="{{ route('clientes.index') }}" class="btn btn-secondary">
                    <i class="bi bi-arrow-left"></i> Cancelar
                </a>
            </div>
        </form>
    </div>
</div>
</div></div>

@push('scripts')
<script>
function detectarTipoCedula(val) {
    val = val.trim();
    const fb = document.getElementById('cedula-feedback');
    const sel = document.getElementById('sel-tipo');

    if (val.length === 0) { fb.textContent = ''; return; }

    if (val.length === 10) {
        // Cédula ecuatoriana — validar dígito verificador
        const valid = validarCedula(val);
        if (valid) {
            fb.innerHTML = '<span class="text-success"><i class="bi bi-check-circle-fill"></i> Cédula válida — Persona Natural</span>';
            sel.value = 'natural';
        } else {
            fb.innerHTML = '<span class="text-danger"><i class="bi bi-x-circle-fill"></i> Cédula inválida</span>';
        }
    } else if (val.length === 13 && val.endsWith('001')) {
        fb.innerHTML = '<span class="text-primary"><i class="bi bi-building"></i> RUC válido — Persona Jurídica</span>';
        sel.value = 'juridico';
    } else if (val.length < 10) {
        fb.innerHTML = `<span class="text-muted">${val.length}/10 dígitos</span>`;
    } else {
        fb.innerHTML = '<span class="text-muted">RUC debe tener 13 dígitos</span>';
    }
}

function validarCedula(cedula) {
    if (!/^\d{10}$/.test(cedula)) return false;
    const provincia = parseInt(cedula.substring(0, 2));
    if (provincia < 1 || provincia > 24) return false;
    const digitos = cedula.split('').map(Number);
    const verificador = digitos[9];
    let suma = 0;
    for (let i = 0; i < 9; i++) {
        let d = digitos[i];
        if (i % 2 === 0) { d *= 2; if (d > 9) d -= 9; }
        suma += d;
    }
    const residuo = suma % 10;
    return residuo === 0 ? verificador === 0 : (10 - residuo) === verificador;
}
</script>
@endpush
@endsection
