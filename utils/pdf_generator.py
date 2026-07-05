import os
from datetime import datetime
from models.factura import FacturaModel
import config


def generar_factura_pdf(factura_id):
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
    except ImportError:
        raise ImportError("Instale reportlab: pip install reportlab")

    factura, items = FacturaModel.obtener_con_detalle(factura_id)
    if not factura:
        raise ValueError(f"Factura {factura_id} no encontrada")

    # Directorio de salida
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'facturas_pdf')
    os.makedirs(out_dir, exist_ok=True)
    filename = os.path.join(out_dir, f"factura_{factura['numero'].replace('/', '-')}.pdf")

    # Página tipo ticket A4 (o usar 8cm de ancho para tickets más pequeños)
    page_w, page_h = A4
    c = canvas.Canvas(filename, pagesize=A4)
    margin = 2 * cm
    y = page_h - margin

    # ── Encabezado empresa ────────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#2D2D2D'))
    c.rect(0, page_h - 3.5 * cm, page_w, 3.5 * cm, fill=True, stroke=False)

    # Franja naranja decorativa
    c.setFillColor(colors.HexColor('#FF6F00'))
    c.rect(0, page_h - 0.35 * cm, page_w, 0.35 * cm, fill=True, stroke=False)

    c.setFillColor(colors.HexColor('#FF6F00'))
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(page_w / 2, page_h - 1.3 * cm, f"🍓 {config.EMPRESA['nombre']}")

    c.setFillColor(colors.white)
    c.setFont('Helvetica', 9)
    c.drawCentredString(page_w / 2, page_h - 2.0 * cm,
                         f"RUC: {config.EMPRESA['ruc']}")
    c.drawCentredString(page_w / 2, page_h - 2.6 * cm,
                         f"{config.EMPRESA['direccion']}  |  Tel: {config.EMPRESA['telefono']}")
    c.drawCentredString(page_w / 2, page_h - 3.1 * cm,
                         f"Email: {config.EMPRESA['email']}")

    y = page_h - 4.2 * cm

    # ── Datos de la factura + cliente ─────────────────────────────────────────
    c.setFillColor(colors.HexColor('#FFF3E0'))
    c.rect(margin, y - 3.0 * cm, page_w - 2 * margin, 3.0 * cm, fill=True, stroke=False)
    c.setStrokeColor(colors.HexColor('#FF6F00'))
    c.setLineWidth(0.8)
    c.rect(margin, y - 3.0 * cm, page_w - 2 * margin, 3.0 * cm, fill=False, stroke=True)

    # Izquierda: número, fecha, tipo
    c.setFillColor(colors.HexColor('#E65100'))
    c.setFont('Helvetica-Bold', 12)
    tipo = factura.get('tipo_comprobante', 'factura').upper()
    c.drawString(margin + 0.3 * cm, y - 0.55 * cm, f"{tipo} N°: {factura['numero']}")

    c.setFont('Helvetica', 9)
    c.setFillColor(colors.black)
    fecha_str = str(factura['fecha'])[:19] if factura['fecha'] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        dt = datetime.strptime(fecha_str[:19], '%Y-%m-%d %H:%M:%S')
        fecha_str = dt.strftime('%d/%m/%Y  %H:%M')
    except Exception:
        pass
    c.drawString(margin + 0.3 * cm, y - 1.1 * cm, f"Fecha: {fecha_str}")
    c.drawString(margin + 0.3 * cm, y - 1.7 * cm, f"Forma de pago: {factura.get('forma_pago','')}")
    c.drawString(margin + 0.3 * cm, y - 2.3 * cm, f"Atendido por: {factura.get('cajero','—')}")

    # Derecha: datos del cliente
    mid = page_w / 2 + 0.5 * cm
    c.setFillColor(colors.HexColor('#E65100'))
    c.setFont('Helvetica-Bold', 9)
    c.drawString(mid, y - 0.55 * cm, 'DATOS DEL CLIENTE')
    c.setFont('Helvetica', 9)
    c.setFillColor(colors.black)
    nombre_cli = f"{factura.get('cliente_nombre','')} {factura.get('cliente_apellido','')}".strip() or 'CONSUMIDOR FINAL'
    c.drawString(mid, y - 1.1 * cm, f"Nombre: {nombre_cli}")
    c.drawString(mid, y - 1.7 * cm, f"Cédula/RUC: {factura.get('cedula','9999999999')}")
    direccion = factura.get('direccion') or ''
    if direccion:
        c.drawString(mid, y - 2.3 * cm, f"Dirección: {direccion[:35]}")

    y -= 3.6 * cm

    # ── Tabla de ítems ─────────────────────────────────────────────────────────
    headers = ['Cant', 'Descripción', 'P. Unit', 'Subtotal']
    data = [headers]
    for it in (items or []):
        data.append([
            str(it['cantidad']),
            it['descripcion'],
            f"$ {float(it['precio_unitario']):.2f}",
            f"$ {float(it['subtotal']):.2f}"
        ])

    col_widths = [1.5 * cm, 10.5 * cm, 2.5 * cm, 2.5 * cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D2D2D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#FFF3E0')]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#BDBDBD')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))

    tw, th = table.wrapOn(c, page_w - 2 * margin, page_h)
    table.drawOn(c, margin, y - th)
    y -= th + 0.5 * cm

    # ── Totales ────────────────────────────────────────────────────────────────
    tot_x = page_w - margin - 6 * cm
    def tot_line(label, valor, bold=False, color='black'):
        nonlocal y
        c.setFont('Helvetica-Bold' if bold else 'Helvetica', 10 if bold else 9)
        c.setFillColor(colors.HexColor('#B71C1C') if bold else colors.black)
        c.drawString(tot_x, y, label)
        c.drawRightString(page_w - margin, y, valor)
        c.setFillColor(colors.black)
        y -= 0.55 * cm

    c.setStrokeColor(colors.HexColor('#BDBDBD'))
    c.line(tot_x, y, page_w - margin, y)
    y -= 0.3 * cm
    tot_line('Subtotal:', f"$ {float(factura['subtotal']):.2f}")
    tot_line(f'IVA {config.IVA_PORCENTAJE}%:', f"$ {float(factura['iva']):.2f}")
    if float(factura['descuento']) > 0:
        tot_line('Descuento:', f"- $ {float(factura['descuento']):.2f}")
    c.line(tot_x, y + 0.1 * cm, page_w - margin, y + 0.1 * cm)
    y -= 0.1 * cm
    tot_line('TOTAL:', f"$ {float(factura['total']):.2f}", bold=True)

    y -= 0.3 * cm
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#555555'))
    c.drawString(margin, y, f"Forma de pago: {factura['forma_pago']}")

    # ── Pie de página ──────────────────────────────────────────────────────────
    y -= 1.2 * cm
    c.setStrokeColor(colors.HexColor('#FF6F00'))
    c.setLineWidth(1.5)
    c.line(margin, y, page_w - margin, y)
    y -= 0.5 * cm
    c.setFont('Helvetica-Bold', 9)
    c.setFillColor(colors.HexColor('#E65100'))
    c.drawCentredString(page_w / 2, y, f'¡Gracias por su compra en {config.EMPRESA["nombre"]}!')
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#555555'))
    c.drawCentredString(page_w / 2, y - 0.45 * cm,
                         f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    c.save()
    return filename


def generar_reporte_ventas_pdf(fecha_ini, fecha_fin, facturas):
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle
    except ImportError:
        raise ImportError("Instale reportlab: pip install reportlab")

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'facturas_pdf')
    os.makedirs(out_dir, exist_ok=True)
    filename = os.path.join(out_dir, f"reporte_{fecha_ini}_{fecha_fin}.pdf")

    page_w, page_h = A4
    c = canvas.Canvas(filename, pagesize=A4)
    margin = 2 * cm
    y = page_h - margin

    c.setFillColor(colors.HexColor('#1a237e'))
    c.rect(0, page_h - 2.5 * cm, page_w, 2.5 * cm, fill=True, stroke=False)
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 14)
    c.drawCentredString(page_w / 2, page_h - 1.6 * cm,
                         f"REPORTE DE VENTAS: {fecha_ini} al {fecha_fin}")

    y = page_h - 3.2 * cm
    total_general = sum(float(f['total']) for f in facturas)
    c.setFillColor(colors.black)
    c.setFont('Helvetica', 10)
    c.drawString(margin, y, f"Total facturas: {len(facturas)}   |   Total ventas: ${total_general:.2f}")
    y -= 0.8 * cm

    headers = ['N° Factura', 'Fecha', 'Cliente', 'Total', 'Pago']
    data = [headers]
    for f in facturas:
        nombre = f'{f.get("cliente_nombre","") or ""} {f.get("cliente_apellido","") or ""}'.strip()
        data.append([
            f['numero'],
            str(f['fecha'])[:10],
            nombre[:30],
            f"${float(f['total']):.2f}",
            f['forma_pago'][:20]
        ])

    col_widths = [4 * cm, 2.5 * cm, 6 * cm, 2.5 * cm, 3 * cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#F5F5F5')]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#BDBDBD')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    tw, th = table.wrapOn(c, page_w - 2 * margin, page_h)
    table.drawOn(c, margin, y - th)

    c.save()
    return filename
