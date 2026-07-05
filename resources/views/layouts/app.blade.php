<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title','Facturación') — TUTI FRUT</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        :root { --navy:#1a237e; --navy2:#283593; }
        body { background:#f0f2f5; font-size:.9rem; }
        /* Sidebar */
        #sidebar { width:220px; min-height:100vh; background:var(--navy); position:fixed; top:0; left:0; z-index:100; }
        #sidebar .brand { background:var(--navy2); padding:16px 14px; border-bottom:1px solid #3949ab; }
        #sidebar .brand h6 { color:#FFD600; font-weight:700; margin:0; font-size:1rem; }
        #sidebar .brand small { color:#90caf9; }
        #sidebar .nav-link { color:rgba(255,255,255,.8); padding:10px 16px; border-radius:0; font-size:.85rem; }
        #sidebar .nav-link:hover, #sidebar .nav-link.active { background:#3949ab; color:#fff; }
        #sidebar .nav-link i { margin-right:8px; width:16px; }
        #sidebar .user-box { position:absolute; bottom:0; width:100%; background:var(--navy2); padding:10px 14px; font-size:.78rem; color:#90caf9; }
        /* Topbar */
        #topbar { margin-left:220px; background:var(--navy); color:#fff; padding:8px 20px; position:sticky; top:0; z-index:99; }
        /* Content */
        #main { margin-left:220px; padding:20px; }
        /* Cards */
        .card { border:none; box-shadow:0 1px 4px rgba(0,0,0,.1); }
        .card-header { background:var(--navy); color:#fff; font-weight:600; padding:10px 16px; }
        /* Tables */
        .table thead th { background:var(--navy); color:#fff; font-size:.8rem; white-space:nowrap; }
        .table tbody tr:hover { background:#e8eaf6; }
        /* Badges */
        .badge-iva { background:#e3f2fd; color:#1565c0; font-size:.7rem; }
        /* Alerts */
        .alert { border-radius:6px; }
        /* Scrollable table */
        .table-wrap { overflow-x:auto; }
        @media(max-width:768px){
            #sidebar{display:none} #main,#topbar{margin-left:0}
        }
    </style>
    @stack('styles')
</head>
<body>

{{-- Sidebar --}}
<nav id="sidebar">
    <div class="brand">
        <h6>🍓 TUTI FRUT</h6>
        <small>Sistema de Facturación</small>
    </div>
    <ul class="nav flex-column mt-2">
        <li class="nav-item">
            <a href="{{ route('facturacion.index') }}"
               class="nav-link {{ request()->is('facturacion*') ? 'active' : '' }}">
                <i class="bi bi-receipt"></i> Facturación
            </a>
        </li>
        <li class="nav-item">
            <a href="{{ route('categorias.index') }}"
               class="nav-link {{ request()->is('categorias*') ? 'active' : '' }}">
                <i class="bi bi-grid-3x3-gap"></i> Categorías
            </a>
        </li>
        <li class="nav-item">
            <a href="{{ route('inventario.index') }}"
               class="nav-link {{ request()->is('inventario*') ? 'active' : '' }}">
                <i class="bi bi-box-seam"></i> Inventario
            </a>
        </li>
        <li class="nav-item">
            <a href="{{ route('clientes.index') }}"
               class="nav-link {{ request()->is('clientes*') ? 'active' : '' }}">
                <i class="bi bi-people"></i> Clientes
            </a>
        </li>
        <li class="nav-item">
            <a href="{{ route('egresos.caja.index') }}"
               class="nav-link {{ request()->is('egresos*') ? 'active' : '' }}">
                <i class="bi bi-cash-stack"></i> Egresos
            </a>
        </li>
        <li class="nav-item">
            <a href="{{ route('reportes.index') }}"
               class="nav-link {{ request()->is('reportes*') ? 'active' : '' }}">
                <i class="bi bi-bar-chart-line"></i> Reportes
            </a>
        </li>
        @if(session('usuario.rol') === 'admin')
        <li class="nav-item">
            <a href="{{ route('usuarios.index') }}"
               class="nav-link {{ request()->is('usuarios*') ? 'active' : '' }}">
                <i class="bi bi-person-gear"></i> Usuarios
            </a>
        </li>
        @endif
    </ul>
    <div class="user-box">
        <i class="bi bi-person-circle"></i>
        <strong>{{ session('usuario.nombre') }}</strong><br>
        {{ strtoupper(session('usuario.rol','')) }}
    </div>
</nav>

{{-- Topbar --}}
<div id="topbar" class="d-flex justify-content-between align-items-center">
    <span class="fw-bold">@yield('title','Dashboard')</span>
    <form action="{{ route('logout') }}" method="POST" class="m-0">
        @csrf
        <button class="btn btn-sm btn-outline-light">
            <i class="bi bi-box-arrow-right"></i> Cerrar Sesión
        </button>
    </form>
</div>

{{-- Main --}}
<main id="main">
    @if(session('success'))
        <div class="alert alert-success alert-dismissible fade show py-2">
            <i class="bi bi-check-circle"></i> {{ session('success') }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    @endif
    @if(session('error'))
        <div class="alert alert-danger alert-dismissible fade show py-2">
            <i class="bi bi-exclamation-triangle"></i> {{ session('error') }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    @endif

    @yield('content')
</main>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
@stack('scripts')
</body>
</html>
