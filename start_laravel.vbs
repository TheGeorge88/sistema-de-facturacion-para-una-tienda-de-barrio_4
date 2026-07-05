Set oShell = CreateObject("WScript.Shell")
oShell.Run "cmd /c cd /d ""C:\Users\DELL\OneDrive\Escritorio\sistema de facturación para una tienda pequeña"" && php artisan serve --port=8000", 0, False
WScript.Sleep 2000
oShell.Run "http://localhost:8000/facturacion", 1, False
