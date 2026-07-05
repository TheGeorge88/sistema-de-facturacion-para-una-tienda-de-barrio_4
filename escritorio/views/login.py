import tkinter as tk
from tkinter import ttk, messagebox
from models.usuario import UsuarioModel


class LoginWindow:
    def __init__(self, on_success):
        self.on_success = on_success
        self.root = tk.Tk()
        self.root.title("TUTI FRUT — Iniciar Sesión")
        self.root.resizable(False, False)
        self._center(420, 540)
        self.root.configure(bg='#1C1C1C')
        self._build()

    def _center(self, w, h):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build(self):
        # ── Marca ────────────────────────────────────────────────────────────
        hdr = tk.Frame(self.root, bg='#1C1C1C', pady=30)
        hdr.pack(fill='x')

        tk.Label(hdr, text='🍓', font=('Arial', 36), bg='#1C1C1C').pack()
        tk.Label(hdr, text='TUTI FRUT',
                 font=('Arial', 30, 'bold'), bg='#1C1C1C', fg='#FF6F00').pack()
        tk.Label(hdr, text='Sistema de Facturación',
                 font=('Arial', 10), bg='#1C1C1C', fg='#9E9E9E').pack(pady=(4, 0))

        # ── Card blanca ───────────────────────────────────────────────────────
        card = tk.Frame(self.root, bg='white', padx=36, pady=34)
        card.pack(fill='both', expand=True, padx=28, pady=(10, 28))

        # Línea de acento naranja arriba del card
        accent = tk.Frame(card, bg='#FF6F00', height=3)
        accent.place(x=0, y=0, relwidth=1)

        tk.Label(card, text='Bienvenido',
                 font=('Arial', 16, 'bold'), bg='white', fg='#212121').pack(pady=(14, 4))
        tk.Label(card, text='Ingresa tus credenciales para continuar',
                 font=('Arial', 9), bg='white', fg='#757575').pack(pady=(0, 22))

        # Usuario
        tk.Label(card, text='USUARIO', font=('Arial', 8, 'bold'),
                 bg='white', fg='#9E9E9E', anchor='w').pack(fill='x')
        self.var_user = tk.StringVar(value='admin')
        ent_user = tk.Entry(card, textvariable=self.var_user,
                            font=('Arial', 12), relief='flat', bd=0,
                            bg='#F5F5F5', fg='#212121',
                            insertbackground='#FF6F00')
        ent_user.pack(fill='x', pady=(4, 16), ipady=10, padx=2)

        # Contraseña
        tk.Label(card, text='CONTRASEÑA', font=('Arial', 8, 'bold'),
                 bg='white', fg='#9E9E9E', anchor='w').pack(fill='x')
        self.var_pw = tk.StringVar()
        ent_pw = tk.Entry(card, textvariable=self.var_pw,
                          font=('Arial', 12), show='●', relief='flat', bd=0,
                          bg='#F5F5F5', fg='#212121',
                          insertbackground='#FF6F00')
        ent_pw.pack(fill='x', pady=(4, 28), ipady=10, padx=2)

        # Botón
        btn = tk.Button(card, text='INGRESAR',
                        font=('Arial', 11, 'bold'),
                        bg='#FF6F00', fg='white', relief='flat', bd=0,
                        cursor='hand2', command=self._login,
                        pady=12,
                        activebackground='#E65100', activeforeground='white')
        btn.pack(fill='x')

        tk.Label(card, text='admin / admin123',
                 font=('Arial', 8), bg='white', fg='#BDBDBD').pack(pady=(14, 0))

        ent_user.focus()
        ent_user.bind('<Return>', lambda e: ent_pw.focus())
        ent_pw.bind('<Return>', lambda e: self._login())

    def _login(self):
        user = self.var_user.get().strip()
        pw   = self.var_pw.get().strip()
        if not user or not pw:
            messagebox.showwarning('Aviso', 'Complete usuario y contraseña.', parent=self.root)
            return
        usuario = UsuarioModel.autenticar(user, pw)
        if usuario:
            self.root.destroy()
            self.on_success(usuario)
        else:
            messagebox.showerror('Error', 'Usuario o contraseña incorrectos.', parent=self.root)
            self.var_pw.set('')

    def run(self):
        self.root.mainloop()
