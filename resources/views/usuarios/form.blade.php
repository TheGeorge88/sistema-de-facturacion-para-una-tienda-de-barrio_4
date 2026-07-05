@extends('layouts.app')
@section('title', isset($usuario) ? 'Editar Usuario' : 'Nuevo Usuario')
@section('content')
<div class="row justify-content-center">
<div class="col-lg-5">
<div class="card">
    <div class="card-header">
        <i class="bi bi-person-gear"></i>
        {{ isset($usuario) ? 'Editar: '.$usuario->nombre : 'Nuevo Usuario' }}
    </div>
    <div class="card-body">
        @if($errors->any())
        <div class="alert alert-danger py-2">
            <ul class="mb-0 ps-3">@foreach($errors->all() as $e)<li>{{ $e }}</li>@endforeach</ul>
        </div>
        @endif

        <form action="{{ isset($usuario) ? route('usuarios.update',$usuario->id) : route('usuarios.store') }}"
              method="POST">
            @csrf
            @if(isset($usuario)) @method('PUT') @endif

            <div class="mb-3">
                <label class="form-label">Nombre completo *</label>
                <input type="text" name="nombre" class="form-control"
                       value="{{ old('nombre',$usuario->nombre ?? '') }}" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Usuario (login) *</label>
                <input type="text" name="usuario" class="form-control"
                       value="{{ old('usuario',$usuario->usuario ?? '') }}" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Contraseña {{ isset($usuario)?'(dejar vacío para no cambiar)':' *' }}</label>
                <input type="password" name="password" class="form-control"
                       {{ isset($usuario)?'':'required' }} minlength="4">
            </div>
            <div class="mb-3">
                <label class="form-label">Rol *</label>
                <select name="rol" class="form-select">
                    <option value="cajero" {{ old('rol',$usuario->rol ?? 'cajero')==='cajero' ? 'selected':'' }}>Cajero</option>
                    <option value="admin"  {{ old('rol',$usuario->rol ?? '')==='admin'  ? 'selected':'' }}>Administrador</option>
                </select>
            </div>
            @if(isset($usuario))
            <div class="mb-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" name="activo" id="activo"
                           {{ $usuario->activo ? 'checked':'' }}>
                    <label class="form-check-label" for="activo">Usuario activo</label>
                </div>
            </div>
            @endif
            <div class="d-flex gap-2">
                <button type="submit" class="btn btn-success">
                    <i class="bi bi-save"></i> Guardar
                </button>
                <a href="{{ route('usuarios.index') }}" class="btn btn-secondary">
                    <i class="bi bi-arrow-left"></i> Cancelar
                </a>
            </div>
        </form>
    </div>
</div>
</div></div>
@endsection
