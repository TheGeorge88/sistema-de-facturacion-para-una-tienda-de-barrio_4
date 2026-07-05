import tkinter as tk
from tkinter import ttk
import config


class MainWindow:
    def __init__(self, usuario):
        self.usuario = usuario
        self.root = tk.Tk()
        self.root.title(f"TUTI FRUT — {usuario['nombre']}")
        self.root.state('zoomed')
        self.root.configure(bg='#F4F6F8')
        self._apply_styles()
        self._build()
        self._show_module('facturacion')

    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#F4F6F8')
        style.configure('Treeview',
                        font=('Segoe UI', 9),
                        rowheight=26,
                        fieldbackground='white',
                        background='white',
                        foreground='#212121')
        style.configure('Treeview.Heading',
                        font=('Segoe UI', 9, 'bold'),
                        background='#2D2D2D',
                        foreground='white',
                        relief='flat',
                        padding=6)
        style.map('Treeview',
                  background=[('selected', '#FF6F00')],
                  foreground=[('selected', 'white')])
        style.configure('TScrollbar',
                        background='#EEEEEE',
                        troughcolor='#FAFAFA',
                        arrowcolor='#9E9E9E',
                        borderwidth=0)
        style.configure('TNotebook',
                        background='#F4F6F8',
                        borderwidth=0)
        style.configure('TNotebook.Tab',
                        font=('Segoe UI', 9, 'bold'),
                        background='#E0E0E0',
                        foreground='#616161',
                        padding=(12, 6))
        style.map('TNotebook.Tab',
                  background=[('selected', '#FF6F00')],
                  foreground=[('selected', 'white')])

    def _build(self):
        # ── Header oscuro ────────────────────────────────────────────────────
        topbar = tk.Frame(self.root, bg='#1C1C1C', height=56)
        topbar.pack(fill='x', side='top')
        topbar.pack_propagate(False)

        # Logo y nombre
        brand = tk.Frame(topbar, bg='#1C1C1C')
        brand.pack(side='left', padx=16, fill='y')
        tk.Label(brand, text='🍓', font=('Arial', 22),
                 bg='#1C1C1C').pack(side='left', padx=(0, 8))
        tk.Label(brand, text='TUTI FRUT',
                 font=('Segoe UI', 15, 'bold'),
                 bg='#1C1C1C', fg='#FF6F00').pack(side='left')
        tk.Label(brand, text='  |  Sistema de Facturación',
                 font=('Segoe UI', 10),
                 bg='#1C1C1C', fg='#616161').pack(side='left')

        # Usuario
        user_frame = tk.Frame(topbar, bg='#1C1C1C')
        user_frame.pack(side='right', padx=16, fill='y')
        tk.Label(user_frame, text=f'👤  {self.usuario["nombre"]}',
                 font=('Segoe UI', 9, 'bold'),
                 bg='#1C1C1C', fg='#EEEEEE').pack(anchor='e')
        tk.Label(user_frame, text=self.usuario['rol'].upper(),
                 font=('Segoe UI', 8),
                 bg='#1C1C1C', fg='#FF6F00').pack(anchor='e')

        # ── Línea de acento naranja ───────────────────────────────────────────
        tk.Frame(self.root, bg='#FF6F00', height=3).pack(fill='x', side='top')

        # ── Navbar gris oscuro ───────────────────────────────────────────────
        navbar = tk.Frame(self.root, bg='#2D2D2D', height=44)
        navbar.pack(fill='x', side='top')
        navbar.pack_propagate(False)

        self.nav_buttons = {}
        modules = [
            ('facturacion', '🧾  Facturación'),
            ('inventario',  '📦  Inventario'),
            ('clientes',    '👥  Clientes'),
            ('egresos',     '💸  Egresos'),
            ('reportes',    '📊  Reportes'),
        ]
        if self.usuario['rol'] == 'admin':
            modules.append(('usuarios', '🔐  Usuarios'))

        for key, label in modules:
            btn = tk.Button(navbar, text=f'  {label}  ',
                            font=('Segoe UI', 9, 'bold'),
                            bg='#2D2D2D', fg='#BDBDBD',
                            relief='flat', bd=0,
                            cursor='hand2',
                            activebackground='#3D3D3D',
                            activeforeground='white',
                            padx=6, pady=11,
                            command=lambda k=key: self._show_module(k))
            btn.pack(side='left')
            self.nav_buttons[key] = btn

        # ── Sombra sutil bajo navbar ─────────────────────────────────────────
        tk.Frame(self.root, bg='#E0E0E0', height=1).pack(fill='x', side='top')

        # ── Contenedor principal ─────────────────────────────────────────────
        self.content = tk.Frame(self.root, bg='#F4F6F8')
        self.content.pack(fill='both', expand=True)
        self.frames = {}

    def _show_module(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(bg='#FF6F00', fg='white')
            else:
                btn.configure(bg='#2D2D2D', fg='#BDBDBD')

        for w in self.content.winfo_children():
            w.destroy()
        self.frames = {}

        if key == 'facturacion':
            from views.facturacion import FacturacionFrame
            frame = FacturacionFrame(self.content, self.usuario)
        elif key == 'inventario':
            from views.inventario import InventarioFrame
            frame = InventarioFrame(self.content, self.usuario)
        elif key == 'clientes':
            from views.clientes import ClientesFrame
            frame = ClientesFrame(self.content)
        elif key == 'egresos':
            from views.egresos import EgresosFrame
            frame = EgresosFrame(self.content, self.usuario)
        elif key == 'reportes':
            from views.reportes import ReportesFrame
            frame = ReportesFrame(self.content, self.usuario)
        elif key == 'usuarios':
            from views.usuarios import UsuariosFrame
            frame = UsuariosFrame(self.content)
        else:
            return
        frame.pack(fill='both', expand=True)

    def run(self):
        self.root.mainloop()
