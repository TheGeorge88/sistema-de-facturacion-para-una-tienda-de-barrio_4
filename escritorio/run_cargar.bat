@echo off
cd /d "%~dp0"
python cargar_productos.py > cargar_output.txt 2>&1
echo Exit code: %ERRORLEVEL% >> cargar_output.txt
