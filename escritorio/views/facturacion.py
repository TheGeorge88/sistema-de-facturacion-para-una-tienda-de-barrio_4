import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from models.producto import ProductoModel
from models.cliente import ClienteModel
from models.factura import FacturaModel
import config


class FacturacionFrame(tk.Frame):
    COL_WIDTHS = {'#': 35, 'IVA': 30, 'CANT': 55, 'CODIGO': 110,
                  'DESCRIPCION': 300, 'V.UNIT': 80, 'V.TOTAL': 90}

    def __init__(self, parent, usuario):
        super().__init__(parent, bg='#F4F6F8')
        self.usuario = usuario
        self.items = []          # lista de dicts en la factura
        self.cliente = None
        self.tipo_comprobante = tk.StringVar(value='factura')
        self.var_descuento = tk.DoubleVar(value=0.0)
        self._formas = {}        # {nombre: (var_bool, var_monto)}
        self._init_cliente_default()
        self._build()
        self._actualizar_numero()

    # ── Inicialización ───────────────────────────────────────────────────────
    def _init_cliente_default(self):
        self.cliente = ClienteModel.consumidor_final()

    def _actualizar_numero(self):
        self.var_num_fact.set(FacturaModel.siguiente_numero())

    # ── Construcción UI ─────────────────────────────────────────────────────
    def _build(self):
        self._build_toolbar()
        self._build_body()
        self._build_bottom()
        self._cargar_inventario()

    def _build_toolbar(self):
        bar = tk.Frame(self, bg='#2D2D2D', pady=5)
        bar.pack(fill='x')

        def btn(parent, text, color, cmd, hover=None):
            b = tk.Button(parent, text=text, font=('Arial', 9, 'bold'),
                          bg=color, fg='white', relief='flat', bd=0,
                          cursor='hand2', padx=10, pady=5,
                          activebackground=hover or color,
                          activeforeground='#FFD600',
                          command=cmd)
            b.pack(side='left', padx=4, pady=2)
            return b

        btn(bar, '🖨  Imprimir / PDF', '#E65100', self._imprimir, '#FF6F00')
        tk.Frame(bar, bg='#E53935', width=1).pack(side='left', fill='y', padx=2, pady=4)
        btn(bar, '🗑  Borrar Todo',    '#C62828', self._borrar_todo,   '#E53935')
        btn(bar, '✂  Borrar Línea',   '#D84315', self._borrar_linea,  '#E64A19')
        tk.Frame(bar, bg='#E53935', width=1).pack(side='left', fill='y', padx=2, pady=4)
        btn(bar, '⛔  Anular Factura', '#6A1B9A', self._anular_factura, '#7B1FA2')
        btn(bar, '🔍  Buscar Factura', '#1565C0', self._buscar_factura, '#1976D2')

        # Número de factura
        tk.Label(bar, text='  FACTURA #:', font=('Arial', 9, 'bold'),
                 bg='#2D2D2D', fg='#FF6F00').pack(side='left', padx=(16, 2))
        self.var_num_fact = tk.StringVar()
        tk.Label(bar, textvariable=self.var_num_fact, font=('Courier', 10, 'bold'),
                 bg='#2D2D2D', fg='white').pack(side='left')

        # Fecha/hora
        self.var_fecha = tk.StringVar()
        tk.Label(bar, textvariable=self.var_fecha, font=('Arial', 9),
                 bg='#2D2D2D', fg='#9E9E9E').pack(side='right', padx=12)
        self._tick()

    def _tick(self):
        self.var_fecha.set(datetime.now().strftime('  %d/%m/%Y  %H:%M:%S  '))
        self.after(1000, self._tick)

    def _build_body(self):
        body = tk.Frame(self, bg='#F4F6F8')
        body.pack(fill='both', expand=True)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=0)
        body.rowconfigure(0, weight=1)

        # ── Panel izquierdo: tabla de factura ────────────────────────────────
        left = tk.Frame(body, bg='white', bd=0)
        left.grid(row=0, column=0, sticky='nsew', padx=(4, 2), pady=4)

        # Barra de búsqueda de producto
        search_row = tk.Frame(left, bg='#F4F6F8', pady=4)
        search_row.pack(fill='x')
        tk.Label(search_row, text='  Código / Nombre producto:',
                 font=('Arial', 9, 'bold'), bg='#F4F6F8', fg='#E53935').pack(side='left')
        self.var_busqueda = tk.StringVar()
        self.ent_busqueda = tk.Entry(search_row, textvariable=self.var_busqueda,
                                     font=('Arial', 11), width=28, relief='solid', bd=1)
        self.ent_busqueda.pack(side='left', padx=6, ipady=4)
        self.ent_busqueda.bind('<Return>', self._agregar_producto)
        self.ent_busqueda.bind('<KeyRelease>', self._autocomplete_key)
        tk.Button(search_row, text=' + Agregar ', font=('Arial', 9, 'bold'),
                  bg='#FF6F00', fg='white', relief='flat', cursor='hand2',
                  command=self._agregar_producto).pack(side='left', padx=4, ipady=4)
        tk.Label(search_row, text='  Cant:', font=('Arial', 9),
                 bg='#F4F6F8').pack(side='left')
        self.var_cantidad = tk.StringVar(value='1')
        tk.Entry(search_row, textvariable=self.var_cantidad,
                 font=('Arial', 10), width=5, relief='solid', bd=1,
                 justify='center').pack(side='left', padx=4, ipady=4)

        # Autocomplete listbox
        self.autocomplete_frame = tk.Frame(left, bg='white', bd=1, relief='solid')
        self.lb_auto = tk.Listbox(self.autocomplete_frame, font=('Arial', 9),
                                   selectbackground='#FF6F00', height=6)
        self.lb_auto.pack(fill='both', expand=True)
        self.lb_auto.bind('<Double-Button-1>', self._select_autocomplete)
        self.lb_auto.bind('<Return>', self._select_autocomplete)
        self._auto_results = []

        # Treeview de factura
        cols = ('#', 'IVA', 'CANT', 'CODIGO', 'DESCRIPCION', 'V.UNIT', 'V.TOTAL')
        tree_frame = tk.Frame(left, bg='white')
        tree_frame.pack(fill='both', expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient='vertical')
        self.tree = ttk.Treeview(tree_frame, columns=cols, show='headings',
                                  yscrollcommand=vsb.set, selectmode='browse',
                                  style='Treeview')
        vsb.configure(command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.pack(fill='both', expand=True)

        widths = [35, 30, 55, 110, 320, 80, 90]
        anchors = ['center', 'center', 'center', 'center', 'w', 'e', 'e']
        for col, w, a in zip(cols, widths, anchors):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=w, anchor=a, stretch=(col == 'DESCRIPCION'))

        self.tree.tag_configure('odd', background='#F5F5F5')
        self.tree.tag_configure('even', background='white')
        self.tree.bind('<Double-Button-1>', self._editar_cantidad)
        self.tree.bind('<Delete>', lambda e: self._borrar_linea())

        # ── Panel derecho: lista de inventario ───────────────────────────────
        right = tk.Frame(body, bg='white', width=180)
        right.grid(row=0, column=1, sticky='nsew', padx=(2, 4), pady=4)
        right.pack_propagate(False)

        tk.Label(right, text='Lista de Inventarios:',
                 font=('Arial', 8, 'bold'), bg='#E53935', fg='white',
                 pady=4).pack(fill='x')

        self.lb_inv = tk.Listbox(right, font=('Arial', 9),
                                  selectbackground='#FF6F00',
                                  selectforeground='white',
                                  activestyle='none')
        sb_inv = ttk.Scrollbar(right, command=self.lb_inv.yview)
        self.lb_inv.configure(yscrollcommand=sb_inv.set)
        sb_inv.pack(side='right', fill='y')
        self.lb_inv.pack(fill='both', expand=True)
        self.lb_inv.bind('<Double-Button-1>', self._agregar_desde_lista)

    def _build_bottom(self):
        bottom = tk.Frame(self, bg='white', bd=0, pady=6)
        bottom.pack(fill='x', padx=4, pady=(0, 4))
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=2)
        bottom.columnconfigure(2, weight=1)

        # ── Formas de pago ────────────────────────────────────────────────────
        fp_frame = tk.LabelFrame(bottom, text='Forma de Pago',
                                  font=('Arial', 9, 'bold'), bg='white',
                                  fg='#E53935', padx=8, pady=4)
        fp_frame.grid(row=0, column=0, sticky='nsew', padx=4)

        formas = ['Efectivo', 'Tarjeta de Crédito', 'Tarjeta de Débito',
                  'Transferencia Bancaria', 'Dinero Electrónico']
        for nombre in formas:
            var_bool = tk.BooleanVar(value=(nombre == 'Efectivo'))
            var_monto = tk.DoubleVar(value=0.0)
            row = tk.Frame(fp_frame, bg='white')
            row.pack(fill='x', pady=1)
            cb = tk.Checkbutton(row, variable=var_bool, bg='white',
                                 command=self._actualizar_pago)
            cb.pack(side='left')
            tk.Label(row, text=nombre, font=('Arial', 8), bg='white',
                     width=16, anchor='w').pack(side='left')
            ent = tk.Entry(row, textvariable=var_monto,
                           font=('Arial', 8), width=7, relief='solid',
                           bd=1, justify='right', state='disabled')
            ent.pack(side='left', padx=2, ipady=2)
            self._formas[nombre] = (var_bool, var_monto, ent)

        # ── Info cliente / tipo ────────────────────────────────────────────────
        mid = tk.Frame(bottom, bg='white')
        mid.grid(row=0, column=1, sticky='nsew', padx=4)

        # Stock bajo
        self.lbl_stock = tk.Label(mid, text='', font=('Arial', 8),
                                   bg='#F4F6F8', fg='#E65100',
                                   wraplength=250, justify='left', padx=4)
        self.lbl_stock.pack(fill='x', pady=2)

        # Cliente
        clt_row = tk.Frame(mid, bg='white')
        clt_row.pack(fill='x', pady=2)
        tk.Label(clt_row, text='Cliente:', font=('Arial', 9, 'bold'),
                 bg='white', fg='#E53935').pack(side='left', padx=(0, 4))
        self.var_cedula = tk.StringVar()
        ent_ced = tk.Entry(clt_row, textvariable=self.var_cedula,
                           font=('Arial', 9), width=14, relief='solid', bd=1)
        ent_ced.pack(side='left', padx=2, ipady=3)
        ent_ced.bind('<Return>', self._buscar_cliente)
        ent_ced.bind('<KeyRelease>', self._cedula_keyrelease)
        tk.Button(clt_row, text='Buscar', font=('Arial', 8),
                  bg='#FF6F00', fg='white', relief='flat', cursor='hand2',
                  command=self._buscar_cliente).pack(side='left', padx=4, ipady=3)
        tk.Button(clt_row, text='Consumidor Final', font=('Arial', 8),
                  bg='#546E7A', fg='white', relief='flat', cursor='hand2',
                  command=self._cliente_final).pack(side='left', padx=2, ipady=3)

        self.lbl_cliente = tk.Label(mid, text='', font=('Arial', 9, 'bold'),
                                     bg='white', fg='#E53935', anchor='w')
        self.lbl_cliente.pack(fill='x', pady=2)
        self._actualizar_lbl_cliente()

        # Descuento
        desc_row = tk.Frame(mid, bg='white')
        desc_row.pack(fill='x', pady=2)
        tk.Label(desc_row, text='Descuento $:', font=('Arial', 9),
                 bg='white').pack(side='left', padx=(0, 4))
        ent_desc = tk.Entry(desc_row, textvariable=self.var_descuento,
                            font=('Arial', 9), width=8, relief='solid', bd=1,
                            justify='right')
        ent_desc.pack(side='left', ipady=3)
        ent_desc.bind('<FocusOut>', lambda e: self._calcular_totales())
        ent_desc.bind('<Return>', lambda e: self._calcular_totales())

        # Tipo comprobante
        tipo_row = tk.Frame(mid, bg='white')
        tipo_row.pack(fill='x', pady=2)
        tk.Label(tipo_row, text='Tipo comprobante:', font=('Arial', 9),
                 bg='white').pack(side='left', padx=(0, 4))
        tk.Radiobutton(tipo_row, text='Factura', variable=self.tipo_comprobante,
                       value='factura', bg='white').pack(side='left', padx=4)
        tk.Radiobutton(tipo_row, text='Recibo', variable=self.tipo_comprobante,
                       value='recibo', bg='white').pack(side='left', padx=4)

        # Botón emitir
        tk.Button(mid, text='  EMITIR FACTURA  ',
                  font=('Arial', 11, 'bold'), bg='#FF6F00', fg='white',
                  relief='flat', cursor='hand2', pady=6,
                  command=self._emitir_factura).pack(fill='x', pady=(8, 2))

        # ── Totales ────────────────────────────────────────────────────────────
        tot_frame = tk.LabelFrame(bottom, text='Totales',
                                   font=('Arial', 9, 'bold'), bg='white',
                                   fg='#E53935', padx=10, pady=6)
        tot_frame.grid(row=0, column=2, sticky='nsew', padx=4)

        def tot_row(label, var, color='#212121', big=False):
            r = tk.Frame(tot_frame, bg='white')
            r.pack(fill='x', pady=2)
            font_lbl = ('Arial', 9)
            font_val = ('Arial', 14 if big else 11, 'bold')
            tk.Label(r, text=label, font=font_lbl, bg='white',
                     width=14, anchor='e').pack(side='left')
            tk.Label(r, textvariable=var, font=font_val, bg='white',
                     fg=color, anchor='e', width=10).pack(side='right')

        self.var_subtotal = tk.StringVar(value='$ 0.00')
        self.var_iva = tk.StringVar(value='$ 0.00')
        self.var_descuento_lbl = tk.StringVar(value='$ 0.00')
        self.var_total = tk.StringVar(value='$ 0.00')

        tot_row(f'SUBTOTAL:', self.var_subtotal)
        tot_row(f'IVA {config.IVA_PORCENTAJE} %:', self.var_iva)
        tot_row('DESCUENTO:', self.var_descuento_lbl, '#E53935')
        tot_row('TOTAL FACT:', self.var_total, '#E53935', big=True)

    # ── Inventario lateral ───────────────────────────────────────────────────
    def _cargar_inventario(self):
        self.lb_inv.delete(0, tk.END)
        prods = ProductoModel.listar()
        self._inv_productos = prods or []
        for p in self._inv_productos:
            self.lb_inv.insert(tk.END, f"{p['descripcion'][:22]} ${p['precio_venta']:.2f}")
        self._check_stock_bajo()

    def _check_stock_bajo(self):
        bajo = ProductoModel.stock_bajo() or []
        if bajo:
            nombres = ', '.join(p['descripcion'][:15] for p in bajo[:3])
            self.lbl_stock.configure(
                text=f'⚠ Stock bajo: {nombres}{"..." if len(bajo) > 3 else ""}',
                bg='#F4F6F8'
            )
        else:
            self.lbl_stock.configure(text='', bg='white')

    def _agregar_desde_lista(self, event=None):
        sel = self.lb_inv.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(self._inv_productos):
            p = self._inv_productos[idx]
            self._add_item(p)

    # ── Búsqueda de productos ─────────────────────────────────────────────────
    def _autocomplete_key(self, event=None):
        termino = self.var_busqueda.get().strip()
        if len(termino) < 2:
            self.autocomplete_frame.place_forget()
            return
        resultados = ProductoModel.buscar(termino) or []
        self._auto_results = resultados
        self.lb_auto.delete(0, tk.END)
        for p in resultados:
            self.lb_auto.insert(tk.END, f"{p['codigo']}  |  {p['descripcion']}  (${p['precio_venta']:.2f})")
        if resultados:
            x = self.ent_busqueda.winfo_x()
            y = self.ent_busqueda.winfo_y() + self.ent_busqueda.winfo_height()
            self.autocomplete_frame.place(in_=self.ent_busqueda.master,
                                           x=x, y=y, width=500, height=130)
            self.autocomplete_frame.lift()
        else:
            self.autocomplete_frame.place_forget()

    def _select_autocomplete(self, event=None):
        sel = self.lb_auto.curselection()
        if not sel:
            return
        p = self._auto_results[sel[0]]
        self.autocomplete_frame.place_forget()
        self.var_busqueda.set('')
        self._add_item(p)

    def _agregar_producto(self, event=None):
        # Si hay autocomplete abierto, seleccionar primero
        if self.autocomplete_frame.winfo_ismapped():
            if self.lb_auto.curselection():
                self._select_autocomplete()
                return
            elif self._auto_results:
                p = self._auto_results[0]
                self.autocomplete_frame.place_forget()
                self.var_busqueda.set('')
                self._add_item(p)
                return

        termino = self.var_busqueda.get().strip()
        if not termino:
            return
        # Búsqueda por código exacto primero
        prod = ProductoModel.por_codigo(termino)
        if prod:
            self.var_busqueda.set('')
            self._add_item(prod)
        else:
            resultados = ProductoModel.buscar(termino) or []
            if len(resultados) == 1:
                self.var_busqueda.set('')
                self._add_item(resultados[0])
            elif resultados:
                self._auto_results = resultados
                self.lb_auto.delete(0, tk.END)
                for p in resultados:
                    self.lb_auto.insert(tk.END, f"{p['codigo']}  |  {p['descripcion']}  (${p['precio_venta']:.2f})")
                x = self.ent_busqueda.winfo_x()
                y = self.ent_busqueda.winfo_y() + self.ent_busqueda.winfo_height()
                self.autocomplete_frame.place(in_=self.ent_busqueda.master,
                                               x=x, y=y, width=500, height=130)
                self.autocomplete_frame.lift()
                self.lb_auto.focus()
            else:
                messagebox.showwarning('No encontrado',
                                        f'Producto "{termino}" no encontrado.',
                                        parent=self.winfo_toplevel())

    def _add_item(self, prod):
        try:
            cantidad = int(self.var_cantidad.get())
            if cantidad < 1:
                cantidad = 1
        except ValueError:
            cantidad = 1
        self.var_cantidad.set('1')

        # Si ya está en la factura, aumentar cantidad
        for item in self.items:
            if item['producto_id'] == prod['id']:
                item['cantidad'] += cantidad
                item['subtotal'] = round(item['precio_unitario'] * item['cantidad'], 2)
                self._redraw_tree()
                self._calcular_totales()
                return

        precio = float(prod['precio_venta'])
        item = {
            'producto_id': prod['id'],
            'codigo': prod['codigo'],
            'descripcion': prod['descripcion'],
            'precio_unitario': precio,
            'tiene_iva': bool(prod['tiene_iva']),
            'cantidad': cantidad,
            'subtotal': round(precio * cantidad, 2)
        }
        self.items.append(item)
        self._redraw_tree()
        self._calcular_totales()
        self.ent_busqueda.focus()

    def _redraw_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for i, item in enumerate(self.items):
            iva_mark = '*' if item['tiene_iva'] else ''
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert('', 'end', iid=str(i), tag=tag, values=(
                i + 1,
                iva_mark,
                item['cantidad'],
                item['codigo'],
                item['descripcion'],
                f"$ {item['precio_unitario']:.2f}",
                f"$ {item['subtotal']:.2f}"
            ))

    # ── Cálculo de totales ────────────────────────────────────────────────────
    def _calcular_totales(self):
        subtotal_sin_iva = 0.0
        subtotal_con_iva = 0.0
        for item in self.items:
            if item['tiene_iva']:
                subtotal_con_iva += item['subtotal']
            else:
                subtotal_sin_iva += item['subtotal']

        base_sin = subtotal_sin_iva
        base_con = subtotal_con_iva / (1 + config.IVA_PORCENTAJE / 100)
        iva = subtotal_con_iva - base_con
        subtotal = base_sin + base_con
        try:
            descuento = float(self.var_descuento.get())
        except Exception:
            descuento = 0.0
        total = subtotal + iva - descuento

        self.var_subtotal.set(f'$ {subtotal:.2f}')
        self.var_iva.set(f'$ {iva:.2f}')
        self.var_descuento_lbl.set(f'$ {descuento:.2f}')
        self.var_total.set(f'$ {total:.2f}')

        # Actualizar forma de pago (efectivo por defecto)
        if 'Efectivo' in self._formas:
            vb, vm, ent = self._formas['Efectivo']
            if vb.get():
                vm.set(round(total, 2))

        return subtotal, iva, descuento, total

    def _actualizar_pago(self):
        for nombre, (vb, vm, ent) in self._formas.items():
            ent.configure(state='normal' if vb.get() else 'disabled')
            if not vb.get():
                vm.set(0.0)
        self._calcular_totales()

    # ── Acciones de la factura ────────────────────────────────────────────────
    def _borrar_linea(self):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        self.items.pop(idx)
        self._redraw_tree()
        self._calcular_totales()

    def _borrar_todo(self):
        if self.items and not messagebox.askyesno(
                'Confirmar', 'Borrar todos los ítems?', parent=self.winfo_toplevel()):
            return
        self.items.clear()
        self._redraw_tree()
        self._init_cliente_default()
        self._actualizar_lbl_cliente()
        self._actualizar_numero()
        self.var_descuento.set(0.0)
        self.var_cedula.set('')
        self.var_busqueda.set('')
        self.tipo_comprobante.set('factura')
        for nombre, (vb, vm, ent) in self._formas.items():
            vb.set(nombre == 'Efectivo')
            vm.set(0.0)
            ent.configure(state='normal' if nombre == 'Efectivo' else 'disabled')
        self._calcular_totales()

    def _editar_cantidad(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        item = self.items[idx]
        nueva = simpledialog.askinteger(
            'Cantidad', f'Nueva cantidad para:\n{item["descripcion"]}',
            initialvalue=item['cantidad'], minvalue=1, parent=self.winfo_toplevel())
        if nueva:
            item['cantidad'] = nueva
            item['subtotal'] = round(item['precio_unitario'] * nueva, 2)
            self._redraw_tree()
            self._calcular_totales()

    # ── Cliente ───────────────────────────────────────────────────────────────
    def _cedula_keyrelease(self, event=None):
        cedula = self.var_cedula.get().strip()
        if len(cedula) >= 10:
            c = ClienteModel.por_cedula(cedula)
            if c:
                self.cliente = c
                self._actualizar_lbl_cliente()
            else:
                self._init_cliente_default()
                self._actualizar_lbl_cliente()

    def _buscar_cliente(self, event=None):
        cedula = self.var_cedula.get().strip()
        if not cedula:
            self._dialogo_buscar_cliente()
            return
        c = ClienteModel.por_cedula(cedula)
        if c:
            self.cliente = c
            self._actualizar_lbl_cliente()
        else:
            if messagebox.askyesno('No encontrado',
                                    f'Cédula {cedula} no registrada.\n¿Desea registrar el cliente?',
                                    parent=self.winfo_toplevel()):
                self._dialogo_nuevo_cliente(cedula)

    def _dialogo_buscar_cliente(self):
        from views.clientes import DialogoBuscarCliente
        dlg = DialogoBuscarCliente(self.winfo_toplevel())
        if dlg.result:
            self.cliente = dlg.result
            self._actualizar_lbl_cliente()

    def _dialogo_nuevo_cliente(self, cedula=''):
        from views.clientes import DialogoCliente
        dlg = DialogoCliente(self.winfo_toplevel(), cedula=cedula)
        if dlg.result:
            self.cliente = dlg.result
            self._actualizar_lbl_cliente()

    def _cliente_final(self):
        self._init_cliente_default()
        self.var_cedula.set('')
        self._actualizar_lbl_cliente()

    def _actualizar_lbl_cliente(self):
        if self.cliente:
            nombre = f"{self.cliente['nombre']} {self.cliente.get('apellido','')}".strip()
            self.lbl_cliente.configure(
                text=f"  {nombre}  |  {self.cliente['cedula']}"
            )
        else:
            self.lbl_cliente.configure(text='  Sin cliente asignado')

    # ── Emitir factura ─────────────────────────────────────────────────────────
    def _emitir_factura(self):
        if not self.items:
            messagebox.showwarning('Aviso', 'Agregue productos a la factura.', parent=self.winfo_toplevel())
            return

        subtotal, iva, descuento, total = self._calcular_totales()

        # Validar pago
        formas_activas = [n for n, (vb, vm, _) in self._formas.items() if vb.get()]
        if not formas_activas:
            messagebox.showwarning('Aviso', 'Seleccione al menos una forma de pago.', parent=self.winfo_toplevel())
            return

        monto_pagado = sum(vm.get() for _, (vb, vm, _) in self._formas.items() if vb.get())
        if monto_pagado < total:
            messagebox.showwarning('Aviso',
                                    f'Monto pagado (${monto_pagado:.2f}) insuficiente.\nTotal: ${total:.2f}',
                                    parent=self.winfo_toplevel())
            return

        forma_pago_str = ', '.join(formas_activas)
        numero = self.var_num_fact.get()

        items_db = [{
            'producto_id': it['producto_id'],
            'descripcion': it['descripcion'],
            'cantidad': it['cantidad'],
            'precio_unitario': it['precio_unitario'],
            'tiene_iva': 1 if it['tiene_iva'] else 0,
            'subtotal': it['subtotal']
        } for it in self.items]

        factura_id = FacturaModel.crear(
            numero=numero,
            cliente_id=self.cliente['id'] if self.cliente else None,
            usuario_id=self.usuario['id'],
            subtotal=round(subtotal, 2),
            iva=round(iva, 2),
            descuento=round(descuento, 2),
            total=round(total, 2),
            forma_pago=forma_pago_str,
            tipo_comprobante=self.tipo_comprobante.get(),
            items=items_db
        )

        if factura_id:
            # Descontar stock
            for it in self.items:
                ProductoModel.actualizar_stock(it['producto_id'], it['cantidad'])

            cambio = round(monto_pagado - total, 2)
            msg = (f"Factura #{numero} emitida exitosamente.\n\n"
                   f"Total: ${total:.2f}\n"
                   f"Recibido: ${monto_pagado:.2f}\n"
                   f"Cambio: ${cambio:.2f}")

            if messagebox.askyesno('Éxito', f'{msg}\n\n¿Generar PDF / imprimir?',
                                    parent=self.winfo_toplevel()):
                self._generar_pdf(factura_id)

            self._borrar_todo()
        else:
            messagebox.showerror('Error', 'No se pudo guardar la factura.', parent=self.winfo_toplevel())

    # ── PDF / impresión ────────────────────────────────────────────────────────
    def _imprimir(self):
        sel = self.tree.selection()
        if not self.items:
            messagebox.showinfo('Info', 'No hay ítems en la factura actual.', parent=self.winfo_toplevel())
            return
        # Generar vista previa del total
        subtotal, iva, descuento, total = self._calcular_totales()
        messagebox.showinfo('Vista previa',
                             f'Factura: {self.var_num_fact.get()}\n'
                             f'Subtotal: ${subtotal:.2f}\n'
                             f'IVA {config.IVA_PORCENTAJE}%: ${iva:.2f}\n'
                             f'Descuento: ${descuento:.2f}\n'
                             f'TOTAL: ${total:.2f}\n\n'
                             'Emita la factura para generar el PDF.',
                             parent=self.winfo_toplevel())

    def _generar_pdf(self, factura_id):
        try:
            from utils.pdf_generator import generar_factura_pdf
            path = generar_factura_pdf(factura_id)
            if path:
                import os
                os.startfile(path)
        except Exception as e:
            messagebox.showerror('Error PDF', str(e), parent=self.winfo_toplevel())

    def _anular_factura(self):
        numero = simpledialog.askstring('Anular Factura', 'Número de factura a anular:',
                                         parent=self.winfo_toplevel())
        if not numero:
            return
        from database.connection import db
        fact = db.fetchone("SELECT * FROM facturas WHERE numero=%s", (numero,))
        if not fact:
            messagebox.showerror('Error', f'Factura {numero} no encontrada.', parent=self.winfo_toplevel())
            return
        if fact['estado'] == 'anulada':
            messagebox.showinfo('Info', 'La factura ya está anulada.', parent=self.winfo_toplevel())
            return
        if messagebox.askyesno('Confirmar', f'¿Anular factura #{numero}?', parent=self.winfo_toplevel()):
            FacturaModel.anular(fact['id'])
            messagebox.showinfo('OK', f'Factura #{numero} anulada.', parent=self.winfo_toplevel())

    def _buscar_factura(self):
        numero = simpledialog.askstring('Buscar Factura', 'Número de factura:',
                                         parent=self.winfo_toplevel())
        if not numero:
            return
        from database.connection import db
        fact = db.fetchone("""
            SELECT f.*, c.nombre AS cli_nombre, c.apellido AS cli_apellido, c.cedula
            FROM facturas f
            LEFT JOIN clientes c ON f.cliente_id = c.id
            WHERE f.numero=%s
        """, (numero,))
        if not fact:
            messagebox.showerror('No encontrada', f'Factura #{numero} no existe.', parent=self.winfo_toplevel())
            return
        items = db.execute("SELECT * FROM detalle_facturas WHERE factura_id=%s", (fact['id'],))
        detalle = '\n'.join(
            f"  {it['cantidad']}x {it['descripcion']}  ${it['subtotal']:.2f}"
            for it in (items or [])
        )
        info = (f"Factura: {fact['numero']}\n"
                f"Fecha: {fact['fecha']}\n"
                f"Cliente: {fact['cli_nombre']} {fact['cli_apellido']}  ({fact['cedula']})\n"
                f"Estado: {fact['estado'].upper()}\n\n"
                f"Ítems:\n{detalle}\n\n"
                f"Subtotal: ${fact['subtotal']:.2f}\n"
                f"IVA: ${fact['iva']:.2f}\n"
                f"Total: ${fact['total']:.2f}")
        messagebox.showinfo(f'Factura #{numero}', info, parent=self.winfo_toplevel())
