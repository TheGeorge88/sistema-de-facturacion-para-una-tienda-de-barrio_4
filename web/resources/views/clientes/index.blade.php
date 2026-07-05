@extends('layouts.app')
@section('title','Clientes')
@section('content')
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <span><i class="bi bi-people"></i> Clientes ({{ $clientes->count() }})</span>
        <a href="{{ route('clientes.create') }}" class="btn btn-success btn-sm">
            <i class="bi bi-plus-lg"></i> Nuevo Cliente
        </a>
    </div>
    <div class="card-body p-2">
        <input type="text" class="form-control form-control-sm mb-2"
               placeholder="Filtrar..." oninput="filtrar(this.value)">
        <div class="table-wrap">
        <table class="table table-sm table-bordered table-hover mb-0" id="tbl-cli">
            <thead>
                <tr><th>Cédula/RUC</th><th>Nombre</th><th>Apellido</th>
                    <th>Teléfono</th><th>Email</th><th>Tipo</th><th>Acc.</th></tr>
            </thead>
            <tbody>
            @forelse($clientes as $c)
            <tr>
                <td>{{ $c->cedula }}</td>
                <td>{{ $c->nombre }}</td>
                <td>{{ $c->apellido }}</td>
                <td>{{ $c->telefono }}</td>
                <td>{{ $c->email }}</td>
                <td><span class="badge bg-info text-dark">{{ ucfirst($c->tipo) }}</span></td>
                <td class="text-center" style="white-space:nowrap">
                    <a href="{{ route('clientes.edit',$c->id) }}" class="btn btn-xs btn-outline-primary py-0 px-1">
                        <i class="bi bi-pencil"></i>
                    </a>
                    @if($c->cedula !== '9999999999')
                    <form action="{{ route('clientes.destroy',$c->id) }}" method="POST" class="d-inline"
                          onsubmit="return confirm('¿Eliminar {{ addslashes($c->nombre) }}?')">
                        @csrf @method('DELETE')
                        <button class="btn btn-xs btn-outline-danger py-0 px-1"><i class="bi bi-trash"></i></button>
                    </form>
                    @endif
                </td>
            </tr>
            @empty
            <tr><td colspan="7" class="text-center py-3 text-muted">Sin clientes registrados</td></tr>
            @endforelse
            </tbody>
        </table>
        </div>
    </div>
</div>
@endsection
@push('scripts')
<script>
function filtrar(q){q=q.toLowerCase();document.querySelectorAll('#tbl-cli tbody tr').forEach(tr=>{tr.style.display=tr.textContent.toLowerCase().includes(q)?'':'none'})}
</script>
@endpush
