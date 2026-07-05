<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Iniciar Sesión — TUTI FRUT</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        body { background:linear-gradient(135deg,#1a237e 0%,#283593 60%,#3949ab 100%); min-height:100vh; display:flex; align-items:center; }
        .login-card { border:none; border-radius:16px; box-shadow:0 8px 32px rgba(0,0,0,.3); }
        .login-header { background:#1a237e; color:#fff; border-radius:16px 16px 0 0; padding:28px; text-align:center; }
        .login-header h4 { color:#FFD600; font-weight:800; margin:0; }
        .login-header small { color:#90caf9; }
        .form-control { border-radius:8px; }
        .btn-login { background:#1a237e; color:#fff; border:none; border-radius:8px; font-weight:700; padding:10px; }
        .btn-login:hover { background:#283593; color:#fff; }
    </style>
</head>
<body>
<div class="container" style="max-width:400px">
    <div class="card login-card">
        <div class="login-header">
            <i class="bi bi-receipt-cutoff" style="font-size:2.5rem"></i>
            <h4 class="mt-2">🍓 TUTI FRUT</h4>
            <small>Sistema de Facturación — Versión Web</small>
        </div>
        <div class="card-body p-4">
            @if(session('error'))
                <div class="alert alert-danger py-2">
                    <i class="bi bi-exclamation-triangle"></i> {{ session('error') }}
                </div>
            @endif
            <form action="/login" method="POST">
                @csrf
                <div class="mb-3">
                    <label class="form-label fw-semibold">Usuario</label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-person"></i></span>
                        <input type="text" name="usuario" class="form-control" value="admin" required autofocus>
                    </div>
                </div>
                <div class="mb-4">
                    <label class="form-label fw-semibold">Contraseña</label>
                    <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-lock"></i></span>
                        <input type="password" name="password" class="form-control" required>
                    </div>
                </div>
                <button type="submit" class="btn btn-login w-100">
                    <i class="bi bi-box-arrow-in-right"></i> INGRESAR
                </button>
            </form>
            <p class="text-center text-muted mt-3 small">admin / admin123</p>
        </div>
    </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
