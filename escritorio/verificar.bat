@echo off
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -u root -pJUANJOSE2021 facturacion_gg < check.sql > check_result.txt 2>&1
type check_result.txt
