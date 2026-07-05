import tkinter as tk
from tkinter import ttk, messagebox
from models.cliente import ClienteModel


def validar_cedula_ec(cedula: str) -> bool:
    """Algoritmo de validación de cédula ecuatoriana (10 dígitos)."""
    if len(cedula) != 10 or not cedula.isdigit():
        return False
    provincia = int(cedula[:2])
    if not (1 <= provincia <= 24):
        return False
    tercero = int(cedula[2])
    if tercero > 5:
        return False
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for i, coef in enumerate(coeficientes):
        val = int(cedula[i]) * coef
        if val >= 10:
            val -= 9
        suma += val
    verificador = (10 - (suma % 10)) % 10
    return verificador == int(cedula[9])


def validar_ruc_ec(ruc: str) -> bool:
    """Validación básica de RUC ecuatoriano (13 dígitos)."""
    if len(ruc) != 13 or not ruc.isdigit():
        return False
    tercero = int(ruc[2])
    if ruc[10:] == '000':
        return False
    if tercero < 6:          # Persona natural: cedula + 001
        return validar_cedula_ec(ruc[:10])
    if tercero == 6:          # Entidad pública
        coef = [3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(ruc[i]) * coef[i] for i in range(8))
        ver  = 11 - (suma % 11)
        if ver >= 10:
            ver = 0
        return ver == int(ruc[8])
    if tercero == 9:          # Persona jurídica / sociedad
        coef = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(ruc[i]) * coef[i] for i in range(9))
        ver  = 11 - (suma % 11)
        if ver >= 10:
            ver = 0
        return ver == int(ruc[9])
    return False


def validar_identificacion(cedula: str) -> tuple[bool, str]:
    """
    Valida cédula (10 dígitos) o RUC (13 dígitos) ecuatoriano.
    Retorna (valido, mensaje_error).
    """
    cedula = cedula.strip()
    if cedula == '9999999999999':    # Consumidor Final SRI
        return True, ''
    if len(cedula) == 10:
        if validar_cedula_ec(cedula):
            return True, ''
        return False, 'La cédula ecuatoriana no es válida.'
    if len(cedula) == 13:
        if validar_ruc_ec(cedula):
            return True, ''
        return False, 'El RUC ecuatoriano no es válido.'
    return False, 'Debe ingresar una cédula (10 dígitos) o RUC (13 dígitos).'


class ClientesFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg='#F4F6F8')
        self._build()
        self._cargar()

    def _build(self):
        bar = tk.Frame(self, bg='#2D2D2D', pady=5)
        bar.pack(fill='x')
        tk.Label(bar, text='  GESTIÓN DE CLIENTES',
                 font=('Arial', 11, 'bold'), bg='#2D2D2D', fg='white').pack(side='left', padx=5)

        def btn(text, color, cmd):
            tk.Button(bar, text=text, font=('Arial', 9, 'bold'),
                      bg=color, fg='white', relief='flat', cursor='hand2',
                      padx=8, pady=4, command=cmd).pack(side='left', padx=4, pady=3)

        btn('+ Nuevo', '#2E7D32', self._nuevo)
        btn('Editar', '#FF6F00', self._editar)
        btn('Eliminar', '#B71C1C', self._eliminar)
        btn('Actualizar', '#546E7A', self._cargar)

        src = tk.Frame(self, bg='#F4F6F8', pady=4)
        src.pack(fill='x', padx=4, pady=(4, 0))
        tk.Label(src, text='Buscar:', font=('Arial', 9), bg='#F4F6F8').pack(side='left', padx=6)
        self.var_busq = tk.StringVar()
        ent = tk.Entry(src, textvariable=self.var_busq, font=('Arial', 10),
                       width=30, relief='solid', bd=1)
        ent.pack(side='left', padx=4, ipady=4)
        ent.bind('<KeyRelease>', lambda e: self._filtrar())

        frame = tk.Frame(self, bg='white')
        frame.pack(fill='both', expand=True, padx=4, pady=4)

        cols = ('ID', 'Cédula/RUC', 'Nombre', 'Apellido', 'Teléfono', 'Email', 'Tipo')
        vsb = ttk.Scrollbar(frame, orient='vertical')
        self.tree = ttk.Treeview(frame, columns=cols, show='headings',
                                  yscrollcommand=vsb.set, selectmode='browse')
        vsb.configure(command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)

        widths = [50, 120, 160, 160, 110, 180, 80]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=40, anchor='center')
        self.tree.column('Nombre', anchor='w')
        self.tree.column('Apellido', anchor='w')

        self.tree.tag_configure('par', background='#F5F5F5')
        self.tree.bind('<Double-Button-1>', lambda e: self._editar())

        self.lbl_total = tk.Label(self, text='', font=('Arial', 9),
                                   bg='#F4F6F8', anchor='w', padx=8)
        self.lbl_total.pack(fill='x')

    def _cargar(self):
        self._todos = ClienteModel.listar() or []
        self._filtrar()

    def _filtrar(self):
        t = self.var_busq.get().strip().lower()
        if t:
            mostrar = [c for c in self._todos
                       if t in c['nombre'].lower()
                       or t in (c['apellido'] or '').lower()
                       or t in c['cedula']]
        else:
            mostrar = self._todos
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, c in enumerate(mostrar):
            self.tree.insert('', 'end', iid=str(c['id']),
                              tag='par' if i % 2 else '',
                              values=(c['id'], c['cedula'], c['nombre'],
                                      c.get('apellido', ''), c.get('telefono', ''),
                                      c.get('email', ''), c['tipo']))
        self.lbl_total.configure(text=f'  Total clientes: {len(mostrar)}')

    def _get_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Aviso', 'Seleccione un cliente.', parent=self.winfo_toplevel())
            return None
        return int(sel[0])

    def _nuevo(self):
        dlg = DialogoCliente(self.winfo_toplevel())
        if dlg.result:
            self._cargar()

    def _editar(self):
        cid = self._get_id()
        if cid is None:
            return
        c = ClienteModel.obtener(cid)
        dlg = DialogoCliente(self.winfo_toplevel(), cliente=c)
        if dlg.result:
            self._cargar()

    def _eliminar(self):
        cid = self._get_id()
        if cid is None:
            return
        c = ClienteModel.obtener(cid)
        if c['cedula'] == '9999999999':
            messagebox.showwarning('Aviso', 'No puede eliminar al Consumidor Final.', parent=self.winfo_toplevel())
            return
        if messagebox.askyesno('Confirmar',
                                f'¿Eliminar cliente: {c["nombre"]} {c["apellido"]}?',
                                parent=self.winfo_toplevel()):
            ClienteModel.eliminar(cid)
            self._cargar()


class DialogoCliente(tk.Toplevel):
    def __init__(self, parent, cliente=None, cedula=''):
        super().__init__(parent)
        self.result = None
        self.cliente = cliente
        self.title('Nuevo Cliente' if cliente is None else 'Editar Cliente')
        self.resizable(False, False)
        self.grab_set()
        self._build(cedula)
        if cliente:
            self._cargar_datos()
        self._center()
        self.wait_window()

    def _center(self):
        self.update_idletasks()
        w, h = 420, 420
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

    def _build(self, cedula_default=''):
        self.configure(bg='white')
        frm = tk.Frame(self, bg='white', padx=20, pady=10)
        frm.pack(fill='both', expand=True)

        pad = {'padx': 6, 'pady': 3}

        def campo(lbl, var, w=30):
            tk.Label(frm, text=lbl, font=('Arial', 9), bg='white', anchor='w').pack(fill='x', **pad)
            e = tk.Entry(frm, textvariable=var, font=('Arial', 10),
                         relief='solid', bd=1, width=w)
            e.pack(fill='x', ipady=4, **pad)
            return e

        self.v_cedula = tk.StringVar(value=cedula_default)
        self.v_nombre = tk.StringVar()
        self.v_apellido = tk.StringVar()
        self.v_dir = tk.StringVar()
        self.v_tel = tk.StringVar()
        self.v_email = tk.StringVar()
        self.v_tipo = tk.StringVar(value='natural')

        campo('Cédula / RUC *', self.v_cedula)
        campo('Nombre *', self.v_nombre)
        campo('Apellido', self.v_apellido)
        campo('Dirección', self.v_dir)

        row2 = tk.Frame(frm, bg='white')
        row2.pack(fill='x', **pad)
        for lbl, var in [('Teléfono', self.v_tel), ('Email', self.v_email)]:
            col = tk.Frame(row2, bg='white')
            col.pack(side='left', fill='x', expand=True, padx=4)
            tk.Label(col, text=lbl, font=('Arial', 9), bg='white').pack(anchor='w')
            tk.Entry(col, textvariable=var, font=('Arial', 10),
                     relief='solid', bd=1).pack(fill='x', ipady=4)

        tipo_row = tk.Frame(frm, bg='white')
        tipo_row.pack(fill='x', **pad)
        tk.Label(tipo_row, text='Tipo:', font=('Arial', 9), bg='white').pack(side='left', padx=4)
        for t, l in [('natural', 'Persona Natural'), ('juridico', 'Persona Jurídica')]:
            tk.Radiobutton(tipo_row, text=l, variable=self.v_tipo, value=t,
                           bg='white', font=('Arial', 9)).pack(side='left', padx=8)

        btn_row = tk.Frame(frm, bg='white')
        btn_row.pack(fill='x', pady=10)
        tk.Button(btn_row, text='Guardar', font=('Arial', 10, 'bold'),
                  bg='#2E7D32', fg='white', relief='flat', cursor='hand2',
                  command=self._guardar, width=12, pady=6).pack(side='left', padx=8)
        tk.Button(btn_row, text='Cancelar', font=('Arial', 10),
                  bg='#546E7A', fg='white', relief='flat', cursor='hand2',
                  command=self.destroy, width=10, pady=6).pack(side='left', padx=4)

    def _cargar_datos(self):
        c = self.cliente
        self.v_cedula.set(c['cedula'])
        self.v_nombre.set(c['nombre'])
        self.v_apellido.set(c.get('apellido', ''))
        self.v_dir.set(c.get('direccion', '') or '')
        self.v_tel.set(c.get('telefono', '') or '')
        self.v_email.set(c.get('email', '') or '')
        self.v_tipo.set(c['tipo'])

    def _guardar(self):
        cedula = self.v_cedula.get().strip()
        nombre = self.v_nombre.get().strip()
        if not cedula or not nombre:
            messagebox.showwarning('Aviso', 'Cédula y Nombre son obligatorios.', parent=self)
            return
        ok, err = validar_identificacion(cedula)
        if not ok:
            messagebox.showwarning('Cédula / RUC inválido', err, parent=self)
            return
        apellido = self.v_apellido.get().strip()
        direccion = self.v_dir.get().strip()
        telefono = self.v_tel.get().strip()
        email = self.v_email.get().strip()
        tipo = self.v_tipo.get()

        if self.cliente:
            ClienteModel.actualizar(
                self.cliente['id'], cedula, nombre, apellido,
                direccion, telefono, email, tipo)
            self.result = ClienteModel.obtener(self.cliente['id'])
        else:
            cid = ClienteModel.crear(cedula, nombre, apellido, direccion, telefono, email, tipo)
            if not cid:
                messagebox.showerror('Error', 'No se pudo guardar. ¿Cédula duplicada?', parent=self)
                return
            self.result = ClienteModel.obtener(cid)
        self.destroy()


class DialogoBuscarCliente(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title('Buscar Cliente')
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self._center()
        self.wait_window()

    def _center(self):
        self.update_idletasks()
        w, h = 500, 340
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

    def _build(self):
        self.configure(bg='white')
        frm = tk.Frame(self, bg='white', padx=10, pady=10)
        frm.pack(fill='both', expand=True)

        src = tk.Frame(frm, bg='white')
        src.pack(fill='x', pady=4)
        tk.Label(src, text='Buscar:', font=('Arial', 9), bg='white').pack(side='left', padx=4)
        self.var_b = tk.StringVar()
        ent = tk.Entry(src, textvariable=self.var_b, font=('Arial', 10),
                       width=28, relief='solid', bd=1)
        ent.pack(side='left', padx=4, ipady=4)
        ent.bind('<KeyRelease>', self._buscar)
        ent.focus()

        cols = ('Cédula', 'Nombre', 'Apellido', 'Teléfono')
        self.tree = ttk.Treeview(frm, columns=cols, show='headings',
                                  height=10, selectmode='browse')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110)
        self.tree.pack(fill='both', expand=True, pady=4)
        self.tree.bind('<Double-Button-1>', self._seleccionar)

        self._clientes = ClienteModel.listar() or []
        self._poblar(self._clientes)

        tk.Button(frm, text='Seleccionar', font=('Arial', 10, 'bold'),
                  bg='#FF6F00', fg='white', relief='flat', cursor='hand2',
                  command=self._seleccionar, pady=5).pack(fill='x', pady=4)

    def _buscar(self, event=None):
        t = self.var_b.get().strip().lower()
        if t:
            mostrar = [c for c in self._clientes
                       if t in c['nombre'].lower() or t in c['cedula']]
        else:
            mostrar = self._clientes
        self._poblar(mostrar)

    def _poblar(self, clientes):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for c in clientes:
            self.tree.insert('', 'end', iid=str(c['id']),
                             values=(c['cedula'], c['nombre'],
                                     c.get('apellido', ''), c.get('telefono', '')))

    def _seleccionar(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        cid = int(sel[0])
        self.result = ClienteModel.obtener(cid)
        self.destroy()

