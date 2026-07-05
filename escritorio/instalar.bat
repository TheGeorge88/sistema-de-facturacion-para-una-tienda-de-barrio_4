@echo off
echo =============================================
echo  INSTALANDO SISTEMA DE FACTURACION GG
echo =============================================
echo.
echo Instalando dependencias Python...
pip install mysql-connector-python reportlab Pillow
echo.
echo =============================================
echo  INSTALACION COMPLETADA
echo  Edite config.py con sus credenciales MySQL
echo  Luego ejecute: ejecutar.bat
echo =============================================
pause
