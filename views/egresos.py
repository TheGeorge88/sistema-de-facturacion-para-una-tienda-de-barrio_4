import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from models.egreso import EgresoCajaModel, EgresoInventarioModel
from database.connection import db


class EgresosFrame(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg='#F4F6F8')
        self.usuario = usuario
        self._build()

    def _build(self):
        bar = tk.Frame(self, bg='#2D2D2D', pady=5)
        bar.pack(fill='x')
        tk.Label(bar, text='  EGRESOS DE CAJA E INVENTARIO',
                 font=('Arial', 11, 'bold'), bg='#B71C1C', fg='white').pack(side='left', padx=5)

        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=4, pady=4)

        self._tab_caja = tk.Frame(nb, bg='#F4F6F8')
        self._tab_inventario = tk.Frame(nb, bg='#F4F6F8')

        nb.add(self._tab_caja,      text='  Egresos de Caja (RF11)  ')
        nb.add(self._tab_inventario, text='  Merma / Autoconsumo (RF12)  ')

        self._build_tab_caja()
        self._build_tab_inventario()

    # ─────────────────────────────────────────────────────────────────────────
    # RF11  EGRESOS DE CAJA
    # ─────────────────────────────────────────────────────────────────────────
    def _build_tab_caja(self):
        tab = self._tab_caja

        # Formulario
        frm = tk.Frame(tab, bg='white', padx=16, pady=12, relief='solid', bd=1)
        frm.pack(fill='x', padx=8, pady=8)
        tk.Label(frm, text='REGISTRAR EGRESO DE CAJA',
                 font=('Arial', 10, 'bold'), bg='white', fg='#B71C1C').grid(
            row=0, column=0, columnspan=4, sticky='w', pady=(0, 8))

        campos = [
            ('Concepto / Descripción *', 'ec_concepto', 'entry', 40),
            ('Monto ($) *',             'ec_monto',    'entry', 12),
            ('Método de pago',          'ec_metodo',   'combo', None),
            ('Observación',             'ec_obs',      'entry', 40),
        ]
        self.ec_concepto = tk.StringVar()
        self.ec_monto    = tk.StringVar()
        self.ec_metodo   = tk.StringVar(value='efectivo')
        self.ec_obs      = tk.StringVar()

        tk.Label(frm, text='Concepto / Descripción *', font=('Arial', 9),
                 bg='white').grid(row=1, column=0, sticky='e', padx=4, pady=3)
        tk.Entry(frm, textvariable=self.ec_concepto, font=('Arial', 10),
                 width=40, relief='solid', bd=1).grid(row=1, column=1, columnspan=3,
                 sticky='w', padx=4, ipady=4)

        tk.Label(frm, text='Monto ($) *', font=('Arial', 9),
                 bg='white').grid(row=2, column=0, sticky='e', padx=4, pady=3)
        tk.Entry(frm, textvariable=self.ec_monto, font=('Arial', 10),
                 width=14, relief='solid', bd=1).grid(row=2, column=1, sticky='w',
                 padx=4, ipady=4)

        tk.Label(frm, text='Método de pago', font=('Arial', 9),
                 bg='white').grid(row=2, column=2, sticky='e', padx=4)
        ttk.Combobox(frm, textvariable=self.ec_metodo, font=('Arial', 9),
                     values=['efectivo', 'transferencia', 'otro'],
                     state='readonly', width=14).grid(row=2, column=3, sticky='w', padx=4)

        tk.Label(frm, text='Observación', font=('Arial', 9),
                 bg='white').grid(row=3, column=0, sticky='e', padx=4, pady=3)
        tk.Entry(frm, textvariable=self.ec_obs, font=('Arial', 10),
                 width=40, relief='solid', bd=1).grid(row=3, column=1, columnspan=3,
                 sticky='w', padx=4, ipady=4)

        tk.Button(frm, text='  REGISTRAR EGRESO  ',
                  font=('Arial', 10, 'bold'), bg='#B71C1C', fg='white',
                  relief='flat', cursor='hand2', pady=6,
                  command=self._guardar_egreso_caja).grid(
            row=4, column=0, columnspan=4, pady=(10, 2))

        # ── Tabla historial ──
        self.lbl_total_caja = tk.Label(tab, text='Total egresos hoy: $0.00',
                                        font=('Arial', 10, 'bold'), bg='#F4F6F8',
                                        fg='#B71C1C')
        self.lbl_total_caja.pack(anchor='e', padx=12)

        cols = ('ID', 'Concepto', 'Monto', 'Método', 'Observación', 'Cajero')
        frm_tree = tk.Frame(tab, bg='white')
        frm_tree.pack(fill='both', expand=True, padx=8, pady=(2, 8))
        vsb = ttk.Scrollbar(frm_tree, orient='vertical')
        self.tree_caja = ttk.Treeview(frm_tree, columns=cols, show='headings',
                                       yscrollcommand=vsb.set, selectmode='browse')
        vsb.configure(command=self.tree_caja.yview)
        vsb.pack(side='right', fill='y')
        self.tree_caja.pack(fill='both', expand=True)
        widths = [40, 280, 80, 100, 200, 120]
        for col, w in zip(cols, widths):
            self.tree_caja.heading(col, text=col)
            self.tree_caja.column(col, width=w, anchor='center' if col not in ('Concepto','Observación') else 'w')

        btn_frame = tk.Frame(tab, bg='#F4F6F8')
        btn_frame.pack(fill='x', padx=8, pady=2)
        tk.Button(btn_frame, text='Eliminar seleccionado',
                  font=('Arial', 9), bg='#C62828', fg='white',
                  relief='flat', cursor='hand2', padx=8, pady=4,
                  command=self._eliminar_egreso_caja).pack(side='right', padx=4)

        self._cargar_egresos_caja()

    def _guardar_egreso_caja(self):
        concepto = self.ec_concepto.get().strip()
        monto_str = self.ec_monto.get().strip().replace(',', '.')
        metodo  = self.ec_metodo.get()
        obs     = self.ec_obs.get().strip()

        if not concepto:
            messagebox.showwarning('Validación', 'Ingrese un concepto.',
                                    parent=self.winfo_toplevel())
            return
        try:
            monto = float(monto_str)
            if monto <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning('Validación', 'Monto inválido.',
                                    parent=self.winfo_toplevel())
            return

        EgresoCajaModel.crear(concepto, monto, metodo, obs, self.usuario['id'])
        messagebox.showinfo('OK', f'Egreso de caja registrado: ${monto:.2f}',
                             parent=self.winfo_toplevel())
        self.ec_concepto.set('')
        self.ec_monto.set('')
        self.ec_obs.set('')
        self._cargar_egresos_caja()

    def _eliminar_egreso_caja(self):
        sel = self.tree_caja.selection()
        if not sel:
            return
        egreso_id = self.tree_caja.item(sel[0])['values'][0]
        if messagebox.askyesno('Confirmar', '¿Eliminar este egreso?',
                                parent=self.winfo_toplevel()):
            EgresoCajaModel.eliminar(egreso_id)
            self._cargar_egresos_caja()

    def _cargar_egresos_caja(self):
        rows = EgresoCajaModel.listar_dia() or []
        for r in self.tree_caja.get_children():
            self.tree_caja.delete(r)
        total = 0.0
        for e in rows:
            self.tree_caja.insert('', 'end', values=(
                e['id'], e['concepto'],
                f"${float(e['monto']):.2f}",
                e['metodo_pago'],
                e.get('observacion', '') or '',
                e.get('cajero', '') or ''
            ))
            total += float(e['monto'])
        self.lbl_total_caja.configure(text=f'Total egresos hoy: ${total:.2f}')

    # ─────────────────────────────────────────────────────────────────────────
    # RF12  EGRESOS DE INVENTARIO (MERMA / AUTOCONSUMO)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_tab_inventario(self):
        tab = self._tab_inventario

        # Formulario
        frm = tk.Frame(tab, bg='white', padx=16, pady=12, relief='solid', bd=1)
        frm.pack(fill='x', padx=8, pady=8)
        tk.Label(frm, text='REGISTRAR EGRESO DE INVENTARIO (MERMA / AUTOCONSUMO)',
                 font=('Arial', 10, 'bold'), bg='white', fg='#E65100').grid(
            row=0, column=0, columnspan=4, sticky='w', pady=(0, 8))

        # Búsqueda de producto
        tk.Label(frm, text='Buscar Producto *', font=('Arial', 9),
                 bg='white').grid(row=1, column=0, sticky='e', padx=4, pady=3)
        self.ei_buscar_var = tk.StringVar()
        self.ei_buscar_var.trace_add('write', self._buscar_productos_ei)
        self.ei_entry_buscar = tk.Entry(frm, textvariable=self.ei_buscar_var,
                                         font=('Arial', 10), width=36,
                                         relief='solid', bd=1)
        self.ei_entry_buscar.grid(row=1, column=1, columnspan=2, sticky='w',
                                   padx=4, ipady=4)

        self.ei_producto_id  = None
        self.ei_lbl_producto = tk.Label(frm, text='Ningún producto seleccionado',
                                         font=('Arial', 9, 'italic'),
                                         bg='white', fg='#546E7A')
        self.ei_lbl_producto.grid(row=1, column=3, padx=4)

        # Listbox de sugerencias
        self.ei_listbox = tk.Listbox(frm, font=('Arial', 9), height=4,
                                      relief='solid', bd=1, exportselection=False)
        self.ei_listbox.grid(row=2, column=1, columnspan=2, sticky='ew', padx=4)
        self.ei_listbox.bind('<<ListboxSelect>>', self._seleccionar_producto_ei)
        self.ei_listbox.grid_remove()

        tk.Label(frm, text='Cantidad *', font=('Arial', 9),
                 bg='white').grid(row=3, column=0, sticky='e', padx=4, pady=3)
        self.ei_cantidad = tk.StringVar(value='1')
        tk.Entry(frm, textvariable=self.ei_cantidad, font=('Arial', 10),
                 width=10, relief='solid', bd=1).grid(row=3, column=1, sticky='w',
                 padx=4, ipady=4)

        tk.Label(frm, text='Motivo *', font=('Arial', 9),
                 bg='white').grid(row=3, column=2, sticky='e', padx=4)
        self.ei_motivo = tk.StringVar(value='merma')
        ttk.Combobox(frm, textvariable=self.ei_motivo, font=('Arial', 9),
                     values=['merma', 'autoconsumo', 'dano', 'otro'],
                     state='readonly', width=14).grid(row=3, column=3, sticky='w', padx=4)

        tk.Label(frm, text='Observación', font=('Arial', 9),
                 bg='white').grid(row=4, column=0, sticky='e', padx=4, pady=3)
        self.ei_obs = tk.StringVar()
        tk.Entry(frm, textvariable=self.ei_obs, font=('Arial', 10),
                 width=50, relief='solid', bd=1).grid(row=4, column=1, columnspan=3,
                 sticky='w', padx=4, ipady=4)

        tk.Button(frm, text='  REGISTRAR EGRESO DE INVENTARIO  ',
                  font=('Arial', 10, 'bold'), bg='#E65100', fg='white',
                  relief='flat', cursor='hand2', pady=6,
                  command=self._guardar_egreso_inv).grid(
            row=5, column=0, columnspan=4, pady=(10, 2))

        # ── Tabla historial ──
        cols = ('ID', 'Código', 'Producto', 'Cantidad', 'Motivo', 'Observación', 'Cajero')
        frm_tree = tk.Frame(tab, bg='white')
        frm_tree.pack(fill='both', expand=True, padx=8, pady=(2, 8))
        vsb = ttk.Scrollbar(frm_tree, orient='vertical')
        self.tree_inv = ttk.Treeview(frm_tree, columns=cols, show='headings',
                                      yscrollcommand=vsb.set, selectmode='browse')
        vsb.configure(command=self.tree_inv.yview)
        vsb.pack(side='right', fill='y')
        self.tree_inv.pack(fill='both', expand=True)
        widths = [40, 80, 280, 70, 90, 200, 120]
        for col, w in zip(cols, widths):
            self.tree_inv.heading(col, text=col)
            self.tree_inv.column(col, width=w,
                                   anchor='center' if col not in ('Producto','Observación') else 'w')

        self._cargar_egresos_inv()

    def _buscar_productos_ei(self, *_):
        q = self.ei_buscar_var.get().strip()
        if len(q) < 2:
            self.ei_listbox.grid_remove()
            return
        rows = db.execute(
            "SELECT id, codigo, descripcion, stock FROM productos "
            "WHERE activo=1 AND (codigo LIKE %s OR descripcion LIKE %s) LIMIT 10",
            (f'%{q}%', f'%{q}%')
        ) or []
        self.ei_listbox.delete(0, 'end')
        self._productos_sugeridos = rows
        for p in rows:
            self.ei_listbox.insert('end',
                f"{p['codigo']}  –  {p['descripcion']}  (stock: {p['stock']})")
        if rows:
            self.ei_listbox.grid()
        else:
            self.ei_listbox.grid_remove()

    def _seleccionar_producto_ei(self, event):
        sel = self.ei_listbox.curselection()
        if not sel:
            return
        p = self._productos_sugeridos[sel[0]]
        self.ei_producto_id = p['id']
        self.ei_buscar_var.set(p['descripcion'])
        self.ei_lbl_producto.configure(
            text=f"Stock actual: {p['stock']}",
            fg='#FF6F00', font=('Arial', 9, 'bold'))
        self.ei_listbox.grid_remove()

    def _guardar_egreso_inv(self):
        if not self.ei_producto_id:
            messagebox.showwarning('Validación', 'Seleccione un producto.',
                                    parent=self.winfo_toplevel())
            return
        try:
            cant = int(self.ei_cantidad.get())
            if cant <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showwarning('Validación', 'Cantidad inválida.',
                                    parent=self.winfo_toplevel())
            return
        motivo = self.ei_motivo.get()
        obs    = self.ei_obs.get().strip()

        # Verificar stock suficiente
        prod = db.fetchone("SELECT stock, descripcion FROM productos WHERE id=%s",
                            (self.ei_producto_id,))
        if prod and prod['stock'] < cant:
            if not messagebox.askyesno(
                    'Stock insuficiente',
                    f"Stock disponible: {prod['stock']}\n"
                    f"Cantidad a dar de baja: {cant}\n\n"
                    "¿Continuar de todas formas?",
                    parent=self.winfo_toplevel()):
                return

        EgresoInventarioModel.crear(
            self.ei_producto_id, cant, motivo, obs, self.usuario['id'])

        messagebox.showinfo('OK',
            f"Egreso registrado:\n{prod['descripcion']}\nCantidad: {cant}  |  Motivo: {motivo}",
            parent=self.winfo_toplevel())

        self.ei_producto_id = None
        self.ei_buscar_var.set('')
        self.ei_cantidad.set('1')
        self.ei_obs.set('')
        self.ei_lbl_producto.configure(text='Ningún producto seleccionado',
                                        fg='#546E7A', font=('Arial', 9, 'italic'))
        self._cargar_egresos_inv()

    def _cargar_egresos_inv(self):
        rows = EgresoInventarioModel.listar_dia() or []
        for r in self.tree_inv.get_children():
            self.tree_inv.delete(r)
        for e in rows:
            self.tree_inv.insert('', 'end', values=(
                e['id'], e.get('codigo', ''), e.get('producto', ''),
                e['cantidad'], e['motivo'],
                e.get('observacion', '') or '',
                e.get('cajero', '') or ''
            ))

