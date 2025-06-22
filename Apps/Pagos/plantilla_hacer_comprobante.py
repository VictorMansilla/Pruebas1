from pytz import timezone
from datetime import datetime
import hashlib
import json
from io import BytesIO

from reportlab.lib.pagesizes import A6
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY


def transformar_utc_ar(fecha):
    # Zona horaria de Argentina
    argentina_tz = timezone('America/Argentina/Buenos_Aires')

    # Convertir la hora UTC a hora argentina
    hora_arg = fecha.astimezone(argentina_tz)

    return hora_arg



#Función para generar el hash de todos los datos del comrpobante
def hashear_comprobante(cliente:str, facturaRelacionada:str, fechafactura:str, vendedor:str, metodoPago:str, montoRecibido:str, transferidoA:str, fechaTransferencia:str) -> str:
    comprobante = {
        'Cliente':cliente,
        'Fecha':'',
        'Hora':'',
        'Vendedor':vendedor,
        'Factura_relacionada':facturaRelacionada,
        'Fecha_factura':fechafactura,
        'Monto_recibido':montoRecibido,
        'Medio_pago':metodoPago,
        'Transferido_a':transferidoA,
        'Fecha_transferencia':fechaTransferencia   
        }
    
    contenido = json.dumps(comprobante, sort_keys=True)
    contenido_hasheado = hashlib.sha256(contenido.encode()).hexdigest()
    return contenido_hasheado



def hacer_comprobante(recibo_pago_db:dict) -> bytes:
    pdf_en_memoria = BytesIO()   # Guardar el pdf en memoria (en lugar de escribir en disco)

    # Crear canvas
    c = canvas.Canvas(pdf_en_memoria, pagesize=A6)
    width, height = A6
    y = height - 20
    
    # Preparar estilos
    styles = getSampleStyleSheet()
    estilo_normal = ParagraphStyle(
        name="NormalJustificado",
        parent=styles['Normal'],
        fontSize=8.5,
        leading=10,
        alignment=TA_LEFT
    )

    nota_estilo = ParagraphStyle(
        name="Nota",
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_JUSTIFY
    )

    # Título
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, y, f"Recibo de Pago n° {recibo_pago_db.recibo_pago_numero}")
    y -= 12

    # Línea
    y -= 8
    c.line(10, y, width - 10, y)
    y -= 10

    # Cliente (posible salto de línea)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(10, y, "Cliente:")
    cliente_parrafo = Paragraph(recibo_pago_db.cliente.cliente_nombre, estilo_normal)
    w, h = cliente_parrafo.wrap(width - 55, 40)
    cliente_parrafo.drawOn(c, 55, y - h + 9)
    y -= max(h, 12) + 2

    # Fecha
    c.setFont("Helvetica", 9)
    c.drawString(10, y, "Fecha:")
    c.drawString(55, y, transformar_utc_ar(recibo_pago_db.fecha).strftime('%d/%m/%y'))
    y -= 12

    # Hora
    c.drawString(10, y, "Hora:")
    c.drawString(55, y, transformar_utc_ar(recibo_pago_db.fecha).strftime('%H:%M'))
    y -= 12

    # Vendedor
    c.drawString(10, y, "Vendedor")
    c.drawString(55, y, recibo_pago_db.vendedor.usuario_nombre)
    y -= 14

    # Factura
    c.drawString(10, y, "Factura Relacionada:")
    c.drawRightString(width - 10, y, recibo_pago_db.factura_relacionada)
    y -= 12

    # Fecha de Factura
    c.drawString(10, y, "Fecha de Factura:")
    c.drawRightString(width - 10, y, datetime.strptime(str(recibo_pago_db.fecha_factura), "%Y-%m-%d").strftime("%d/%m/%Y"))
    y -= 12

    # Monto Recibido
    c.drawString(10, y, "Monto Recibido:")
    c.drawRightString(width - 10, y, recibo_pago_db.monto_recibido)
    y -= 10

    # Línea
    y -= 6
    c.line(10, y, width - 10, y)
    y -= 12

    # Medio de pago
    c.drawString(10, y, "Medio de Pago:")
    c.drawString(80, y, recibo_pago_db.medio_de_pago)
    y -= 12

    # Transferido a
    c.drawString(10, y, "✓ Transferido a:")
    c.drawString(80, y, recibo_pago_db.transferido_a if recibo_pago_db.transferido_a else "__________________________________")
    y -= 14

    # Fecha transferencia
    c.drawString(10, y, "Fecha de Transferencia")
    c.drawString(115, y, recibo_pago_db.fecha_transferencia if recibo_pago_db.fecha_transferencia else "__________________________________")
    y -= 14

    # Línea
    c.line(10, y, width - 10, y)
    y -= 12

    # Hash del recibo
    c.drawString(10, y, "🔒 Hach del Recibo:")
    y -= 10
    c.setFont("Helvetica", 7)
    c.drawString(15, y, recibo_pago_db.recibo_hasheado)
    y -= 10

    # Línea
    c.setFont("Helvetica", 9)
    c.line(10, y, width - 10, y)
    y -= 8

    # Nota final
    nota_parrafo = Paragraph("Este documento sirve como constancia de pago recibido por los servicios o productos mencionados. Guarde este comprobante para futuras referencias.", nota_estilo)
    w, h = nota_parrafo.wrap(width - 20, 50)
    nota_parrafo.drawOn(c, 10, y - h)
    y -= h

    # Guardar
    c.save()

    pdf_en_memoria.seek(0)  # Ir al inicio del archivo
    
    return pdf_en_memoria