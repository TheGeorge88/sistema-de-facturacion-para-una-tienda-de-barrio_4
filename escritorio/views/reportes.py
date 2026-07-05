import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from models.factura import FacturaModel
from models.egreso import EgresoCajaModel
import config


class ReportesFrame(tk.Frame):
    def __init__(self, parent, usuario):
        super().__init__(parent, bg='#F4F6F8')
        self.usuario = usuario
        self._build()

    def _build(self):
        bar = tk.Frame(self, bg='#2D2D2D', pady=5)
        bar.pack(fill='x')
        tk.Label(bar, text='  REPORTES Y CIERRE DE CAJA',
                 font=('Arial', 11, 'bold'), bg='#2D2D2D', fg='white').pack(side='left', padx=5)

        # Tabs
        nb = ttk.Notebook(self)
        nb.pack(fill='both', expand=True, padx=4, pady=4)

        self._tab_dia = tk.Frame(nb, bg='#F4F6F8')
        self._tab_rango = tk.Frame(nb, bg='#F4F6F8')
        self._tab_productos = tk.Frame(nb, bg='#F4F6F8')
        self._tab_cierre = tk.Frame(nb, bg='#F4F6F8')

        nb.add(self._tab_dia, text='  Ventas del Día  ')
        nb.add(self._tab_rango, text='  Por Período  ')
        nb.add(self._tab_productos, text='  Más Vendidos  ')
        nb.add(self._tab_cierre, text='  Cierre de Caja  ')

        self._build_tab_dia()
        self._build_tab_rango()
        self._build_tab_productos()
        self._build_tab_cierre()
        self._cargar_dia()

    # ── Ventas del día ────────────────────────────────────────────────────────
    def _build_tab_dia(self):
        tab = self._tab_dia
        ctrl = tk.Frame(tab, bg='#F4F6F8', pady=4)
        ctrl.pack(fill='x', padx=4, pady=4)
        tk.Label(ctrl, text='Fecha:', font=('Arial', 9), bg='#F4F6F8').pack(side='left', padx=6)
        self.var_fecha_dia = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        tk.Entry(ctrl, textvariable=self.var_fecha_dia, font=('Arial', 10),
                 width=12, relief='solid', bd=1, justify='center').pack(side='left', padx=4, ipady=4)
        tk.Button(ctrl, text='Consultar', font=('Arial', 9, 'bold'),
                  bg='#FF6F00', fg='white', relief='flat', cursor='hand2',
                  command=self._cargar_dia, padx=8, pady=4).pack(side='left', padx=4)
        tk.Button(ctrl, text='Hoy', font=('Arial', 9),
                  bg='#546E7A', fg='white', relief='flat', cursor='hand2',
                  command=lambda: (self.var_fecha_dia.set(date.today().strftime('%Y-%m-%d')),
                                   self._cargar_dia()),
                  padx=6, pady=4).pack(side='left', padx=2)

        # Resumen tarjetas
        self.frm_resumen = tk.Frame(tab, bg='#F4F6F8')
        self.frm_resumen.pack(fill='x', padx=4, pady=2)

        # Tabla facturas
        cols = ('N° Factura', 'Hora', 'Cliente', 'Subtotal', 'IVA', 'Descuento', 'Total', 'Pago', 'Estado')
        frm_tree = tk.Frame(tab, bg='white')
        frm_tree.pack(fill='both', expand=True, padx=4, pady=4)
        vsb = ttk.Scrollbar(frm_tree, orient='vertical')
        self.tree_dia = ttk.Treeview(frm_tree, columns=cols, show='headings',
                                      yscrollcommand=vsb.set, selectmode='browse')
        vsb.configure(command=self.tree_dia.yview)
        vsb.pack(side='right', fill='y')
        self.tree_dia.pack(fill='both', expand=True)
        widths = [130, 70, 180, 80, 70, 80, 80, 120, 65]
        for col, w in zip(cols, widths):
            self.tree_dia.heading(col, text=col)
            self.tree_dia.column(col, width=w, anchor='center')
        self.tree_dia.column('Cliente', anchor='w')
        self.tree_dia.tag_configure('anulada', foreground='#B71C1C')

    def _cargar_dia(self):
        fecha = self.var_fecha_dia.get().strip()
        facturas = FacturaModel.listar_dia(fecha) or []
        resumen = FacturaModel.resumen_dia(fecha) or {}
        self._poblar_resumen(resumen)
        for r in self.tree_dia.get_children():
            self.tree_dia.delete(r)
        for f in facturas:
            hora = str(f['fecha']).split(' ')[1][:8] if f['fecha'] else ''
            cliente = f'{f["cliente_nombre"] or ""} {f["cliente_apellido"] or ""}'.strip()
            tag = 'anulada' if f['estado'] == 'anulada' else ''
            self.tree_dia.insert('', 'end', tag=tag, values=(
                f['numero'], hora, cliente,
                f"${f['subtotal']:.2f}", f"${f['iva']:.2f}",
                f"${f['descuento']:.2f}", f"${f['total']:.2f}",
                f['forma_pago'], f['estado'].upper()
            ))

    def _poblar_resumen(self, r):
        for w in self.frm_resumen.winfo_children():
            w.destroy()
        cards = [
            ('Facturas', r.get('num_facturas', 0), '#FF6F00'),
            ('Subtotal', f"${float(r.get('total_subtotal', 0)):.2f}", '#2E7D32'),
            (f'IVA {config.IVA_PORCENTAJE}%', f"${float(r.get('total_iva', 0)):.2f}", '#E65100'),
            ('Descuento', f"${float(r.get('total_descuento', 0)):.2f}", '#6A1B9A'),
            ('TOTAL', f"${float(r.get('total_ventas', 0)):.2f}", '#B71C1C'),
        ]
        for titulo, valor, color in cards:
            card = tk.Frame(self.frm_resumen, bg=color, padx=12, pady=6)
            card.pack(side='left', padx=4, pady=4)
            tk.Label(card, text=titulo, font=('Arial', 8), bg=color, fg='white').pack()
            tk.Label(card, text=str(valor), font=('Arial', 13, 'bold'),
                     bg=color, fg='white').pack()

    # ── Por período ────────────────────────────────────────────────────────────
    def _build_tab_rango(self):
        tab = self._tab_rango
        ctrl = tk.Frame(tab, bg='#F4F6F8', pady=4)
        ctrl.pack(fill='x', padx=4, pady=4)
        tk.Label(ctrl, text='Desde:', font=('Arial', 9), bg='#F4F6F8').pack(side='left', padx=6)
        self.var_ini = tk.StringVar(value=(date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
        tk.Entry(ctrl, textvariable=self.var_ini, font=('Arial', 10),
                 width=12, relief='solid', bd=1, justify='center').pack(side='left', padx=4, ipady=4)
        tk.Label(ctrl, text='Hasta:', font=('Arial', 9), bg='#F4F6F8').pack(side='left', padx=4)
        self.var_fin = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        tk.Entry(ctrl, textvariable=self.var_fin, font=('Arial', 10),
                 width=12, relief='solid', bd=1, justify='center').pack(side='left', padx=4, ipady=4)
        tk.Button(ctrl, text='Consultar', font=('Arial', 9, 'bold'),
                  bg='#FF6F00', fg='white', relief='flat', cursor='hand2',
                  command=self._cargar_rango, padx=8, pady=4).pack(side='left', padx=4)

        self.frm_resumen_r = tk.Frame(tab, bg='#F4F6F8')
        self.frm_resumen_r.pack(fill='x', padx=4, pady=2)

        cols = ('N° Factura', 'Fecha', 'Cliente', 'Subtotal', 'IVA', 'Total', 'Pago')
        frm_tree = tk.Frame(tab, bg='white')
        frm_tree.pack(fill='both', expand=True, padx=4, pady=4)
        vsb = ttk.Scrollbar(frm_tree, orient='vertical')
        self.tree_rango = ttk.Treeview(frm_tree, columns=cols, show='headings',
                                        yscrollcommand=vsb.set, selectmode='browse')
        vsb.configure(command=self.tree_rango.yview)
        vsb.pack(side='right', fill='y')
        self.tree_rango.pack(fill='both', expand=True)
        widths = [130, 100, 180, 80, 70, 80, 120]
        for col, w in zip(cols, widths):
            self.tree_rango.heading(col, text=col)
            self.tree_rango.column(col, width=w, anchor='center')
        self.tree_rango.column('Cliente', anchor='w')

    def _cargar_rango(self):
        fi = self.var_ini.get().strip()
        ff = self.var_fin.get().strip()
        facturas = FacturaModel.listar_rango(fi, ff) or []
        for r in self.tree_rango.get_children():
            self.tree_rango.delete(r)
        total_v = 0.0
        for f in facturas:
            cliente = f'{f["cliente_nombre"] or ""} {f["cliente_apellido"] or ""}'.strip()
            self.tree_rango.insert('', 'end', values=(
                f['numero'],
                str(f['fecha'])[:10],
                cliente,
                f"${f['subtotal']:.2f}",
                f"${f['iva']:.2f}",
                f"${f['total']:.2f}",
                f['forma_pago']
            ))
            total_v += float(f['total'])
        for w in self.frm_resumen_r.winfo_children():
            w.destroy()
        for titulo, valor, color in [
            ('Facturas', len(facturas), '#FF6F00'),
            ('Total Ventas', f'${total_v:.2f}', '#2E7D32')
        ]:
            card = tk.Frame(self.frm_resumen_r, bg=color, padx=12, pady=6)
            card.pack(side='left', padx=4, pady=4)
            tk.Label(card, text=titulo, font=('Arial', 8), bg=color, fg='white').pack()
            tk.Label(card, text=str(valor), font=('Arial', 13, 'bold'),
                     bg=color, fg='white').pack()

    # ── Más vendidos ───────────────────────────────────────────────────────────
    def _build_tab_productos(self):
        tab = self._tab_productos
        ctrl = tk.Frame(tab, bg='#F4F6F8', pady=4)
        ctrl.pack(fill='x', padx=4, pady=4)
        tk.Label(ctrl, text='Desde:', font=('Arial', 9), bg='#F4F6F8').pack(side='left', padx=6)
        self.var_mv_ini = tk.StringVar(value=(date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
        tk.Entry(ctrl, textvariable=self.var_mv_ini, font=('Arial', 10),
                 width=12, relief='solid', bd=1, justify='center').pack(side='left', padx=4, ipady=4)
        tk.Label(ctrl, text='Hasta:', font=('Arial', 9), bg='#F4F6F8').pack(side='left')
        self.var_mv_fin = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        tk.Entry(ctrl, textvariable=self.var_mv_fin, font=('Arial', 10),
                 width=12, relief='solid', bd=1, justify='center').pack(side='left', padx=4, ipady=4)
        tk.Button(ctrl, text='Consultar', font=('Arial', 9, 'bold'),
                  bg='#FF6F00', fg='white', relief='flat', cursor='hand2',
                  command=self._cargar_vendidos, padx=8, pady=4).pack(side='left', padx=4)

        cols = ('Descripción', 'Unidades Vendidas', 'Total Ventas')
        frm_tree = tk.Frame(tab, bg='white')
        frm_tree.pack(fill='both', expand=True, padx=4, pady=4)
        vsb = ttk.Scrollbar(frm_tree, orient='vertical')
        self.tree_mv = ttk.Treeview(frm_tree, columns=cols, show='headings',
                                     yscrollcommand=vsb.set)
        vsb.configure(command=self.tree_mv.yview)
        vsb.pack(side='right', fill='y')
        self.tree_mv.pack(fill='both', expand=True)
        widths = [380, 130, 130]
        for col, w in zip(cols, widths):
            self.tree_mv.heading(col, text=col)
            self.tree_mv.column(col, width=w, anchor='center')
        self.tree_mv.column('Descripción', anchor='w')

    def _cargar_vendidos(self):
        fi = self.var_mv_ini.get().strip()
        ff = self.var_mv_fin.get().strip()
        rows = FacturaModel.productos_mas_vendidos(fi, ff, 20) or []
        for r in self.tree_mv.get_children():
            self.tree_mv.delete(r)
        for row in rows:
            self.tree_mv.insert('', 'end', values=(
                row['descripcion'],
                row['total_vendido'],
                f"${float(row['total_ventas']):.2f}"
            ))

    # ── Cierre de caja ─────────────────────────────────────────────────────────
    def _build_tab_cierre(self):
        tab = self._tab_cierre
        frm = tk.Frame(tab, bg='white', padx=20, pady=10)
        frm.pack(side='left', fill='y')

        tk.Label(frm, text='CIERRE DE CAJA DEL DÍA',
                 font=('Arial', 12, 'bold'), bg='white', fg='#2D2D2D').pack(pady=(0, 10))

        resumen = FacturaModel.resumen_dia() or {}
        total   = float(resumen.get('total_ventas', 0))
        num     = resumen.get('num_facturas', 0)
        egresos = EgresoCajaModel.total_dia()
        neto    = total - egresos

        info = [
            ('Fecha:',             date.today().strftime('%d/%m/%Y')),
            ('Facturas del día:',  str(num)),
            ('Total ventas:',      f'${total:.2f}'),
            ('Egresos de caja:',   f'${egresos:.2f}'),
            ('CAJA NETA:',         f'${neto:.2f}'),
        ]
        for lbl, val in info:
            r = tk.Frame(frm, bg='white')
            r.pack(fill='x', pady=3)
            tk.Label(r, text=lbl, font=('Arial', 10), bg='white',
                     width=20, anchor='w').pack(side='left')
            tk.Label(r, text=val, font=('Arial', 11, 'bold'), bg='white',
                     fg='#2D2D2D').pack(side='left')

        tk.Label(frm, text='Observaciones:', font=('Arial', 9), bg='white').pack(anchor='w', pady=(10, 2))
        self.txt_obs = tk.Text(frm, height=3, width=30, font=('Arial', 9),
                               relief='solid', bd=1)
        self.txt_obs.pack(fill='x')

        tk.Button(frm, text='REGISTRAR CIERRE DE CAJA',
                  font=('Arial', 10, 'bold'), bg='#B71C1C', fg='white',
                  relief='flat', cursor='hand2', pady=8,
                  command=self._registrar_cierre).pack(fill='x', pady=(16, 4))

        # Historial de cierres
        hist_frame = tk.Frame(tab, bg='white')
        hist_frame.pack(fill='both', expand=True, padx=(4, 4), pady=4)
        tk.Label(hist_frame, text='Historial de Cierres',
                 font=('Arial', 10, 'bold'), bg='white', fg='#2D2D2D').pack(pady=4)

        cols = ('Fecha', 'Cajero', 'Efectivo', 'Tarjeta', 'Otros', 'Total', '# Facturas')
        vsb = ttk.Scrollbar(hist_frame, orient='vertical')
        self.tree_cierre = ttk.Treeview(hist_frame, columns=cols, show='headings',
                                         yscrollcommand=vsb.set, height=12)
        vsb.configure(command=self.tree_cierre.yview)
        vsb.pack(side='right', fill='y')
        self.tree_cierre.pack(fill='both', expand=True)
        widths = [90, 140, 90, 90, 80, 90, 80]
        for col, w in zip(cols, widths):
            self.tree_cierre.heading(col, text=col)
            self.tree_cierre.column(col, width=w, anchor='center')
        self._cargar_historial()

    def _registrar_cierre(self):
        resumen = FacturaModel.resumen_dia() or {}
        total   = float(resumen.get('total_ventas', 0))
        num     = int(resumen.get('num_facturas', 0) or 0)
        egresos = EgresoCajaModel.total_dia()
        neto    = total - egresos
        obs     = self.txt_obs.get('1.0', 'end').strip()

        if not messagebox.askyesno('Confirmar Cierre',
                                    f'¿Registrar cierre de caja?\n\n'
                                    f'Total ventas:    ${total:.2f}\n'
                                    f'Egresos caja:  - ${egresos:.2f}\n'
                                    f'CAJA NETA:       ${neto:.2f}\n'
                                    f'Facturas: {num}',
                                    parent=self.winfo_toplevel()):
            return

        FacturaModel.guardar_cierre(
            usuario_id=self.usuario['id'],
            total_efectivo=neto,
            total_tarjeta=0,
            total_otros=0,
            total_general=neto,
            num_facturas=num,
            obs=obs
        )
        messagebox.showinfo('OK', 'Cierre de caja registrado correctamente.',
                             parent=self.winfo_toplevel())
        self._cargar_historial()
        self.txt_obs.delete('1.0', 'end')

    def _cargar_historial(self):
        cierres = FacturaModel.listar_cierres() or []
        for r in self.tree_cierre.get_children():
            self.tree_cierre.delete(r)
        for c in cierres:
            self.tree_cierre.insert('', 'end', values=(
                str(c['fecha']),
                c.get('cajero', ''),
                f"${float(c['total_efectivo']):.2f}",
                f"${float(c['total_tarjeta']):.2f}",
                f"${float(c['total_otros']):.2f}",
                f"${float(c['total_general']):.2f}",
                c['num_facturas']
            ))

