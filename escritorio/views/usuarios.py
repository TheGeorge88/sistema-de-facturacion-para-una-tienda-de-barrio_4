import tkinter as tk
from tkinter import ttk, messagebox
from models.usuario import UsuarioModel


class UsuariosFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#F4F6F8')
        self._build()
        self._cargar()

    def _build(self):
        bar = tk.Frame(self, bg='#2D2D2D', pady=5)
        bar.pack(fill='x')
        tk.Label(bar, text='  GESTIÓN DE USUARIOS',
                 font=('Arial', 11, 'bold'), bg='#2D2D2D', fg='white').pack(side='left', padx=5)

        def btn(text, color, cmd):
            tk.Button(bar, text=text, font=('Arial', 9, 'bold'),
                      bg=color, fg='white', relief='flat', cursor='hand2',
                      padx=8, pady=4, command=cmd).pack(side='left', padx=4, pady=3)

        btn('+ Nuevo', '#2E7D32', self._nuevo)
        btn('Editar', '#FF6F00', self._editar)
        btn('Cambiar Contraseña', '#E65100', self._cambiar_pw)
        btn('Actualizar', '#546E7A', self._cargar)

        frame = tk.Frame(self, bg='white')
        frame.pack(fill='both', expand=True, padx=4, pady=8)

        cols = ('ID', 'Nombre', 'Usuario', 'Rol', 'Estado')
        vsb = ttk.Scrollbar(frame, orient='vertical')
        self.tree = ttk.Treeview(frame, columns=cols, show='headings',
                                  yscrollcommand=vsb.set, height=15,
                                  selectmode='browse')
        vsb.configure(command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)
        widths = [50, 200, 140, 100, 80]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor='center')
        self.tree.column('Nombre', anchor='w')
        self.tree.bind('<Double-Button-1>', lambda e: self._editar())

    def _cargar(self):
        usuarios = UsuarioModel.listar() or []
        for r in self.tree.get_children():
            self.tree.delete(r)
        for u in usuarios:
            self.tree.insert('', 'end', iid=str(u['id']), values=(
                u['id'], u['nombre'], u['usuario'],
                u['rol'].upper(), 'Activo' if u['activo'] else 'Inactivo'
            ))

    def _get_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Aviso', 'Seleccione un usuario.', parent=self.winfo_toplevel())
            return None
        return int(sel[0])

    def _nuevo(self):
        dlg = DialogoUsuario(self.winfo_toplevel())
        if dlg.result:
            self._cargar()

    def _editar(self):
        uid = self._get_id()
        if uid is None:
            return
        u = UsuarioModel.obtener(uid)
        dlg = DialogoUsuario(self.winfo_toplevel(), usuario=u)
        if dlg.result:
            self._cargar()

    def _cambiar_pw(self):
        uid = self._get_id()
        if uid is None:
            return
        pw = tk.simpledialog.askstring('Nueva Contraseña', 'Ingrese la nueva contraseña:',
                                        show='*', parent=self.winfo_toplevel())
        if pw and len(pw) >= 4:
            UsuarioModel.cambiar_password(uid, pw)
            messagebox.showinfo('OK', 'Contraseña actualizada.', parent=self.winfo_toplevel())


class DialogoUsuario(tk.Toplevel):
    def __init__(self, parent, usuario=None):
        super().__init__(parent)
        self.result = None
        self.usuario = usuario
        self.title('Nuevo Usuario' if usuario is None else 'Editar Usuario')
        self.resizable(False, False)
        self.grab_set()
        self._build()
        if usuario:
            self._cargar()
        self._center()
        self.wait_window()

    def _center(self):
        self.update_idletasks()
        w, h = 380, 320
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

    def _build(self):
        self.configure(bg='white')
        frm = tk.Frame(self, bg='white', padx=20, pady=10)
        frm.pack(fill='both', expand=True)
        pad = {'padx': 6, 'pady': 4}

        def campo(lbl, var, show=None):
            tk.Label(frm, text=lbl, font=('Arial', 9), bg='white', anchor='w').pack(fill='x', **pad)
            kw = {'show': show} if show else {}
            tk.Entry(frm, textvariable=var, font=('Arial', 10),
                     relief='solid', bd=1, **kw).pack(fill='x', ipady=4, **pad)

        self.v_nombre = tk.StringVar()
        self.v_usuario = tk.StringVar()
        self.v_pw = tk.StringVar()
        self.v_rol = tk.StringVar(value='cajero')

        campo('Nombre completo *', self.v_nombre)
        campo('Usuario (login) *', self.v_usuario)
        if not self.usuario:
            campo('Contraseña *', self.v_pw, show='*')

        rol_row = tk.Frame(frm, bg='white')
        rol_row.pack(fill='x', **pad)
        tk.Label(rol_row, text='Rol:', font=('Arial', 9), bg='white').pack(side='left', padx=4)
        for v, l in [('cajero', 'Cajero'), ('admin', 'Administrador')]:
            tk.Radiobutton(rol_row, text=l, variable=self.v_rol, value=v,
                           bg='white').pack(side='left', padx=8)

        btn_row = tk.Frame(frm, bg='white')
        btn_row.pack(fill='x', pady=12)
        tk.Button(btn_row, text='Guardar', font=('Arial', 10, 'bold'),
                  bg='#2E7D32', fg='white', relief='flat', cursor='hand2',
                  command=self._guardar, width=12, pady=6).pack(side='left', padx=8)
        tk.Button(btn_row, text='Cancelar', font=('Arial', 10),
                  bg='#546E7A', fg='white', relief='flat', cursor='hand2',
                  command=self.destroy, width=10, pady=6).pack(side='left', padx=4)

    def _cargar(self):
        u = self.usuario
        self.v_nombre.set(u['nombre'])
        self.v_usuario.set(u['usuario'])
        self.v_rol.set(u['rol'])

    def _guardar(self):
        nombre = self.v_nombre.get().strip()
        usuario = self.v_usuario.get().strip()
        if not nombre or not usuario:
            messagebox.showwarning('Aviso', 'Nombre y Usuario son obligatorios.', parent=self)
            return
        if self.usuario:
            UsuarioModel.actualizar(self.usuario['id'], nombre, usuario,
                                     self.v_rol.get(), 1)
        else:
            pw = self.v_pw.get().strip()
            if len(pw) < 4:
                messagebox.showwarning('Aviso', 'Contraseña debe tener al menos 4 caracteres.', parent=self)
                return
            uid = UsuarioModel.crear(nombre, usuario, pw, self.v_rol.get())
            if not uid:
                messagebox.showerror('Error', 'No se pudo crear. ¿Usuario duplicado?', parent=self)
                return
        self.result = True
        self.destroy()

