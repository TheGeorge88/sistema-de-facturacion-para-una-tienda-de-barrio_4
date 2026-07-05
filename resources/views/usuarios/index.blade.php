@extends('layouts.app')
@section('title','Usuarios')
@section('content')
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <span><i class="bi bi-person-gear"></i> Usuarios del Sistema</span>
        <a href="{{ route('usuarios.create') }}" class="btn btn-success btn-sm">
            <i class="bi bi-plus-lg"></i> Nuevo Usuario
        </a>
    </div>
    <div class="card-body p-2">
        <table class="table table-sm table-bordered table-hover mb-0">
            <thead><tr>
                <th>Nombre</th><th>Usuario</th><th>Rol</th><th>Estado</th><th>Acc.</th>
            </tr></thead>
            <tbody>
            @forelse($usuarios as $u)
            <tr class="{{ !$u->activo ? 'table-secondary text-muted':'' }}">
                <td>{{ $u->nombre }}</td>
                <td>{{ $u->usuario }}</td>
                <td><span class="badge {{ $u->rol==='admin'?'bg-danger':'bg-primary' }}">
                    {{ strtoupper($u->rol) }}</span></td>
                <td><span class="badge {{ $u->activo?'bg-success':'bg-secondary' }}">
                    {{ $u->activo?'Activo':'Inactivo' }}</span></td>
                <td>
                    <a href="{{ route('usuarios.edit',$u->id) }}" class="btn btn-xs btn-outline-primary py-0 px-1">
                        <i class="bi bi-pencil"></i>
                    </a>
                    <form action="{{ route('usuarios.destroy',$u->id) }}" method="POST" class="d-inline"
                          onsubmit="return confirm('¿Desactivar usuario {{ addslashes($u->usuario) }}?')">
                        @csrf @method('DELETE')
                        <button class="btn btn-xs btn-outline-danger py-0 px-1"><i class="bi bi-person-dash"></i></button>
                    </form>
                </td>
            </tr>
            @empty
            <tr><td colspan="5" class="text-center py-3 text-muted">Sin usuarios</td></tr>
            @endforelse
            </tbody>
        </table>
    </div>
</div>
@endsection
