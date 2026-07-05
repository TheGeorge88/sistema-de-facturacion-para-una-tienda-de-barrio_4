import tkinter as tk
from tkinter import ttk, messagebox
from models.producto import ProductoModel


class InventarioFrame(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg='#F4F6F8')
        self.usuario = usuario
        self._build()
        self._cargar()

    def _build(self):
        # Barra de acciones
        bar = tk.Frame(self, bg='#2D2D2D', pady=5)
        bar.pack(fill='x')
        tk.Label(bar, text='  INVENTARIO DE PRODUCTOS',
                 font=('Arial', 11, 'bold'), bg='#2D2D2D', fg='white').pack(side='left', padx=5)

        def btn(text, color, cmd):
            tk.Button(bar, text=text, font=('Arial', 9, 'bold'),
                      bg=color, fg='white', relief='flat', cursor='hand2',
                      padx=8, pady=4, command=cmd).pack(side='left', padx=4, pady=3)

        btn('+ Nuevo', '#2E7D32', self._nuevo)
        btn('Editar', '#FF6F00', self._editar)
        btn('Eliminar', '#B71C1C', self._eliminar)
        btn('Actualizar', '#546E7A', self._cargar)

        # Búsqueda
        src = tk.Frame(self, bg='#F4F6F8', pady=4)
        src.pack(fill='x', padx=4, pady=(4, 0))
        tk.Label(src, text='Buscar:', font=('Arial', 9), bg='#F4F6F8').pack(side='left', padx=6)
        self.var_busq = tk.StringVar()
        ent = tk.Entry(src, textvariable=self.var_busq, font=('Arial', 10),
                       width=30, relief='solid', bd=1)
        ent.pack(side='left', padx=4, ipady=4)
        ent.bind('<KeyRelease>', lambda e: self._filtrar())
        tk.Label(src, text='  (* = IVA incluido en precio)',
                 font=('Arial', 8), bg='#F4F6F8', fg='#555').pack(side='left', padx=10)

        # Tabla
        frame = tk.Frame(self, bg='white')
        frame.pack(fill='both', expand=True, padx=4, pady=4)

        cols = ('ID', 'Código', 'Descripción', 'Categoría', 'P.Compra',
                'P.Venta', 'P.Mayor', 'Stock', 'Mín', 'IVA', 'Estado')
        vsb = ttk.Scrollbar(frame, orient='vertical')
        hsb = ttk.Scrollbar(frame, orient='horizontal')
        self.tree = ttk.Treeview(frame, columns=cols, show='headings',
                                  yscrollcommand=vsb.set, xscrollcommand=hsb.set,
                                  selectmode='browse')
        vsb.configure(command=self.tree.yview)
        hsb.configure(command=self.tree.xview)
        hsb.pack(side='bottom', fill='x')
        vsb.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)

        widths = [40, 110, 280, 100, 80, 80, 80, 60, 50, 40, 60]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col,
                               command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, minwidth=40, anchor='center')
        self.tree.column('Descripción', anchor='w')

        self.tree.tag_configure('bajo', background='#FFEBEE')
        self.tree.tag_configure('ok', background='white')
        self.tree.tag_configure('par', background='#F5F5F5')
        self.tree.bind('<Double-Button-1>', lambda e: self._editar())

        # Pie
        self.lbl_total = tk.Label(self, text='', font=('Arial', 9),
                                   bg='#F4F6F8', anchor='w', padx=8)
        self.lbl_total.pack(fill='x')

    def _cargar(self):
        self._todos = ProductoModel.listar(solo_activos=False) or []
        self._filtrar()

    def _filtrar(self):
        termino = self.var_busq.get().strip().lower()
        if termino:
            mostrar = [p for p in self._todos
                       if termino in p['descripcion'].lower() or termino in p['codigo'].lower()]
        else:
            mostrar = self._todos
        self._poblar(mostrar)

    def _poblar(self, productos):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, p in enumerate(productos):
            tag = 'bajo' if p['stock'] <= p['stock_minimo'] and p['activo'] else ('par' if i % 2 else 'ok')
            self.tree.insert('', 'end', iid=str(p['id']), tag=tag, values=(
                p['id'],
                p['codigo'],
                p['descripcion'],
                p.get('categoria', '') or '',
                f"$ {p['precio_compra']:.2f}",
                f"$ {p['precio_venta']:.2f}",
                f"$ {p['precio_mayorista']:.2f}",
                p['stock'],
                p['stock_minimo'],
                'Sí' if p['tiene_iva'] else 'No',
                'Activo' if p['activo'] else 'Inactivo'
            ))
        activos = sum(1 for p in productos if p['activo'])
        bajo = sum(1 for p in productos if p['stock'] <= p['stock_minimo'] and p['activo'])
        self.lbl_total.configure(
            text=f'  Total: {len(productos)} productos  |  Activos: {activos}  |  Stock bajo: {bajo}'
        )

    def _sort(self, col):
        pass

    def _get_selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Aviso', 'Seleccione un producto.', parent=self.winfo_toplevel())
            return None
        return int(sel[0])

    def _nuevo(self):
        dlg = DialogoProducto(self.winfo_toplevel())
        if dlg.result:
            self._cargar()

    def _editar(self):
        pid = self._get_selected_id()
        if pid is None:
            return
        prod = ProductoModel.obtener(pid)
        dlg = DialogoProducto(self.winfo_toplevel(), producto=prod)
        if dlg.result:
            self._cargar()

    def _eliminar(self):
        pid = self._get_selected_id()
        if pid is None:
            return
        prod = ProductoModel.obtener(pid)
        if not messagebox.askyesno('Confirmar',
                                    f'¿Eliminar producto:\n{prod["descripcion"]}?',
                                    parent=self.winfo_toplevel()):
            return
        ProductoModel.eliminar(pid)
        self._cargar()


class DialogoProducto(tk.Toplevel):
    def __init__(self, parent, producto=None):
        super().__init__(parent)
        self.result = None
        self.producto = producto
        self.title('Nuevo Producto' if producto is None else 'Editar Producto')
        self.resizable(False, False)
        self.grab_set()
        self._build()
        if producto:
            self._cargar_datos()
        self._center()
        self.wait_window()

    def _center(self):
        self.update_idletasks()
        w, h = 480, 500
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f'{w}x{h}+{x}+{y}')

    def _build(self):
        self.configure(bg='white')
        pad = {'padx': 10, 'pady': 4}

        frm = tk.Frame(self, bg='white', padx=20, pady=10)
        frm.pack(fill='both', expand=True)

        def row(label, var, **kwargs):
            tk.Label(frm, text=label, font=('Arial', 9), bg='white',
                     anchor='w').pack(fill='x', **pad)
            ent = tk.Entry(frm, textvariable=var, font=('Arial', 10),
                           relief='solid', bd=1, **kwargs)
            ent.pack(fill='x', ipady=4, **pad)
            return ent

        self.v_codigo = tk.StringVar()
        self.v_desc = tk.StringVar()
        self.v_pcompra = tk.StringVar(value='0.00')
        self.v_pventa = tk.StringVar(value='0.00')
        self.v_pmayor = tk.StringVar(value='0.00')
        self.v_stock = tk.StringVar(value='0')
        self.v_min = tk.StringVar(value='5')
        self.v_iva = tk.BooleanVar(value=True)

        row('Código de Barras / Referencia *', self.v_codigo)
        row('Descripción *', self.v_desc)

        # Categoría
        cats = ProductoModel.listar_categorias() or []
        self._cats = {c['nombre']: c['id'] for c in cats}
        tk.Label(frm, text='Categoría', font=('Arial', 9), bg='white',
                 anchor='w').pack(fill='x', **pad)
        self.v_cat = tk.StringVar(value=cats[0]['nombre'] if cats else '')
        cb_cat = ttk.Combobox(frm, textvariable=self.v_cat,
                               values=[c['nombre'] for c in cats],
                               state='readonly', font=('Arial', 10))
        cb_cat.pack(fill='x', ipady=4, **pad)

        # Precios
        prow = tk.Frame(frm, bg='white')
        prow.pack(fill='x', **pad)
        for lbl, var in [('P.Compra $', self.v_pcompra),
                          ('P.Venta $', self.v_pventa),
                          ('P.Mayorista $', self.v_pmayor)]:
            col = tk.Frame(prow, bg='white')
            col.pack(side='left', fill='x', expand=True, padx=4)
            tk.Label(col, text=lbl, font=('Arial', 8), bg='white').pack()
            tk.Entry(col, textvariable=var, font=('Arial', 10),
                     relief='solid', bd=1, width=9, justify='right').pack(ipady=4)

        # Stock
        srow = tk.Frame(frm, bg='white')
        srow.pack(fill='x', **pad)
        for lbl, var in [('Stock actual', self.v_stock), ('Stock mínimo', self.v_min)]:
            col = tk.Frame(srow, bg='white')
            col.pack(side='left', fill='x', expand=True, padx=4)
            tk.Label(col, text=lbl, font=('Arial', 8), bg='white').pack()
            tk.Entry(col, textvariable=var, font=('Arial', 10),
                     relief='solid', bd=1, width=9, justify='center').pack(ipady=4)

        tk.Checkbutton(frm, text='Tiene IVA (12%)', variable=self.v_iva,
                       bg='white', font=('Arial', 9)).pack(anchor='w', padx=10, pady=4)

        # Botones
        btn_row = tk.Frame(frm, bg='white')
        btn_row.pack(fill='x', pady=10)
        tk.Button(btn_row, text='Guardar', font=('Arial', 10, 'bold'),
                  bg='#2E7D32', fg='white', relief='flat', cursor='hand2',
                  command=self._guardar, width=12, pady=6).pack(side='left', padx=8)
        tk.Button(btn_row, text='Cancelar', font=('Arial', 10),
                  bg='#546E7A', fg='white', relief='flat', cursor='hand2',
                  command=self.destroy, width=10, pady=6).pack(side='left', padx=4)

    def _cargar_datos(self):
        p = self.producto
        self.v_codigo.set(p['codigo'])
        self.v_desc.set(p['descripcion'])
        self.v_pcompra.set(str(p['precio_compra']))
        self.v_pventa.set(str(p['precio_venta']))
        self.v_pmayor.set(str(p['precio_mayorista']))
        self.v_stock.set(str(p['stock']))
        self.v_min.set(str(p['stock_minimo']))
        self.v_iva.set(bool(p['tiene_iva']))

    def _guardar(self):
        codigo = self.v_codigo.get().strip()
        desc = self.v_desc.get().strip()
        if not codigo or not desc:
            messagebox.showwarning('Aviso', 'Código y Descripción son obligatorios.', parent=self)
            return
        try:
            pc = float(self.v_pcompra.get())
            pv = float(self.v_pventa.get())
            pm = float(self.v_pmayor.get())
            st = int(self.v_stock.get())
            mn = int(self.v_min.get())
        except ValueError:
            messagebox.showwarning('Aviso', 'Verifique los valores numéricos.', parent=self)
            return

        cat_id = self._cats.get(self.v_cat.get())
        iva = 1 if self.v_iva.get() else 0

        if self.producto:
            ProductoModel.actualizar(
                self.producto['id'], codigo, desc, cat_id, pc, pv, pm, st, mn, iva)
        else:
            pid = ProductoModel.crear(codigo, desc, cat_id, pc, pv, pm, st, mn, iva)
            if not pid:
                messagebox.showerror('Error', 'No se pudo guardar. ¿Código duplicado?', parent=self)
                return
        self.result = True
        self.destroy()

