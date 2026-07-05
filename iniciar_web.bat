@echo off
cd /d "%~dp0"
start /B "C:\PHP-8.5\php.exe" artisan serve --port=8000 >nul 2>&1
timeout /t 2 /nobreak >nul
start http://localhost:8000/facturacion
