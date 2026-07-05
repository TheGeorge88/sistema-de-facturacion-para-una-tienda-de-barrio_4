import sys
import os
import tkinter as tk
from tkinter import messagebox

# Asegura que el directorio raiz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verificar_dependencias():
    faltantes = []
    try:
        import mysql.connector
    except ImportError:
        faltantes.append('mysql-connector-python')
    try:
        from reportlab.pdfgen import canvas
    except ImportError:
        faltantes.append('reportlab')
    return faltantes


def main():
    # Verificar dependencias antes de iniciar GUI
    faltantes = verificar_dependencias()
    if faltantes:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            'Dependencias faltantes',
            f'Instale las siguientes librerías antes de ejecutar:\n\n'
            + '\n'.join(f'  • {d}' for d in faltantes)
            + '\n\nEjecute:  pip install ' + ' '.join(faltantes)
            + '\n\nO doble-clic en  instalar.bat'
        )
        root.destroy()
        sys.exit(1)

    # Configurar base de datos
    from database.connection import db
    ok = db.setup_database()
    if not ok:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            'Error de Conexión MySQL',
            'No se pudo conectar a MySQL.\n\n'
            'Verifique que:\n'
            '  1. MySQL está ejecutándose\n'
            '  2. Las credenciales en config.py son correctas\n\n'
            'Edite el archivo config.py para cambiar\n'
            'usuario, contraseña y host.'
        )
        root.destroy()
        sys.exit(1)

    # Iniciar login
    from views.login import LoginWindow

    def on_login(usuario):
        from views.main_window import MainWindow
        app = MainWindow(usuario)
        app.run()

    login = LoginWindow(on_success=on_login)
    login.run()


if __name__ == '__main__':
    main()
