"""
Utilidades para generar PDFs
"""

from io import BytesIO
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse

# ReportLab imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image, PageBreak, Frame, PageTemplate
)
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


class CertificateGenerator:
    """
    Generador de certificados de capacitación en PDF
    """

    def __init__(self, employee_training):
        self.employee_training = employee_training
        self.employee = employee_training.employee
        self.course = employee_training.schedule.course
        self.schedule = employee_training.schedule

    def generate(self):
        """Genera el certificado en PDF"""
        buffer = BytesIO()

        # Create PDF
        doc = SimpleDocDocument(buffer, pagesize=A4, title=f'Certificado - {self.employee.get_full_name()}')

        # Container for the 'Flowable' objects
        elements = []

        # Add content
        elements.extend(self._build_certificate_content())

        # Build PDF
        doc.build(elements, onFirstPage=self._add_certificate_background)

        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def _build_certificate_content(self):
        """Construye el contenido del certificado"""
        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=32,
            textColor=HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.black,
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=15,
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=20
        )

        # Add spacer for top margin
        elements.append(Spacer(1, 2*inch))

        # Title
        elements.append(Paragraph("CERTIFICADO DE CAPACITACIÓN", title_style))
        elements.append(Spacer(1, 0.3*inch))

        # Company name
        elements.append(Paragraph(f"<b>{settings.COMPANY_FULL_NAME}</b>", subtitle_style))
        elements.append(Spacer(1, 0.5*inch))

        # Certificate text
        cert_text = f"""
        Se certifica que <b>{self.employee.get_full_name()}</b><br/>
        identificado(a) con el código de empleado <b>{self.employee.employee_id or 'N/A'}</b><br/><br/>
        ha completado satisfactoriamente el curso de capacitación:<br/>
        <b>{self.course.name}</b><br/>
        ({self.course.code})<br/><br/>
        con una duración de <b>{self.course.duration_hours} horas</b><br/>
        y una calificación de <b>{self.employee_training.score}/100</b>
        """

        elements.append(Paragraph(cert_text, body_style))
        elements.append(Spacer(1, 0.5*inch))

        # Certificate details table
        details_data = [
            ['Fecha de Emisión:', self.employee_training.certificate_issue_date.strftime('%d de %B de %Y')],
            ['Fecha de Vencimiento:', self.employee_training.certificate_expiry_date.strftime('%d de %B de %Y')],
            ['Número de Certificado:', self.employee_training.certificate_number],
            ['Instructor:', self.schedule.instructor],
        ]

        details_table = Table(details_data, colWidths=[3*inch, 3*inch])
        details_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#667eea')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(details_table)
        elements.append(Spacer(1, inch))

        # Signature section
        signature_data = [
            ['_' * 40, '_' * 40],
            ['Firma del Instructor', 'Firma del Responsable'],
            [self.schedule.instructor, 'Gerente de Operaciones'],
        ]

        signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
        ]))

        elements.append(signature_table)

        return elements

    def _add_certificate_background(self, canvas, doc):
        """Añade el fondo y marco decorativo al certificado"""
        canvas.saveState()

        # Draw border
        canvas.setStrokeColor(HexColor('#667eea'))
        canvas.setLineWidth(3)
        canvas.rect(0.5*inch, 0.5*inch, 7.27*inch, 10.19*inch)

        # Draw inner border
        canvas.setStrokeColor(HexColor('#764ba2'))
        canvas.setLineWidth(1)
        canvas.rect(0.65*inch, 0.65*inch, 6.97*inch, 9.89*inch)

        # Add logo (if exists)
        # logo_path = settings.STATIC_ROOT / 'img' / 'logo.png'
        # if logo_path.exists():
        #     canvas.drawImage(str(logo_path), 0.75*inch, 10*inch, width=1*inch, height=0.5*inch)

        # Add watermark
        canvas.setFont('Helvetica', 60)
        canvas.setFillColor(colors.lightgrey)
        canvas.setFillAlpha(0.1)
        canvas.saveState()
        canvas.translate(4.135*inch, 5.5*inch)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "TR&RS")
        canvas.restoreState()

        canvas.restoreState()

    def get_response(self):
        """Retorna HttpResponse con el PDF"""
        pdf = self.generate()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificado_{self.employee.employee_id}_{self.employee_training.certificate_number}.pdf"'
        response.write(pdf)

        return response


class ServiceReportGenerator:
    """
    Generador de reportes de servicio en PDF
    """

    def __init__(self, service_order):
        self.service_order = service_order

    def generate(self):
        """Genera el reporte de servicio en PDF"""
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        elements = []

        # Add content
        elements.extend(self._build_report_content())

        # Build PDF
        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def _build_report_content(self):
        """Construye el contenido del reporte"""
        elements = []
        styles = getSampleStyleSheet()

        # Header
        header_data = [
            ['TR&RS - REPORTE DE SERVICIO', f'N° {self.service_order.order_number}'],
        ]

        header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#667eea')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))

        elements.append(header_table)
        elements.append(Spacer(1, 0.3*inch))

        # Service Information
        elements.append(Paragraph('<b>INFORMACIÓN DEL SERVICIO</b>', styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))

        service_data = [
            ['Tipo de Servicio:', self.service_order.service_type.name],
            ['Cliente:', self.service_order.client_name],
            ['Contacto:', self.service_order.client_contact],
            ['Ubicación:', self.service_order.location],
            ['Pozo:', self.service_order.well_name or 'N/A'],
            ['Fecha de Inicio:', self.service_order.start_date.strftime('%d/%m/%Y %H:%M')],
            ['Estado:', self.service_order.get_status_display()],
            ['Prioridad:', self.service_order.get_priority_display()],
        ]

        service_table = Table(service_data, colWidths=[2*inch, 4.5*inch])
        service_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        elements.append(service_table)
        elements.append(Spacer(1, 0.3*inch))

        # Description
        elements.append(Paragraph('<b>DESCRIPCIÓN DEL SERVICIO</b>', styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(self.service_order.description, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

        # Team (if exists)
        team = self.service_order.serviceteam_set.all()
        if team.exists():
            elements.append(Paragraph('<b>EQUIPO ASIGNADO</b>', styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))

            team_data = [['Nombre', 'Rol', 'Horas Trabajadas']]
            for member in team:
                team_data.append([
                    member.employee.get_full_name(),
                    member.get_role_display(),
                    str(member.hours_worked)
                ])

            team_table = Table(team_data, colWidths=[3*inch, 2*inch, 1.5*inch])
            team_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(team_table)
            elements.append(Spacer(1, 0.2*inch))

        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer_text = f"Reporte generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}"
        elements.append(Paragraph(footer_text, ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )))

        return elements

    def get_response(self):
        """Retorna HttpResponse con el PDF"""
        pdf = self.generate()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_servicio_{self.service_order.order_number}.pdf"'
        response.write(pdf)

        return response


class InventoryReportGenerator:
    """
    Generador de reportes de inventario en PDF
    """

    def __init__(self, items, title="Reporte de Inventario"):
        self.items = items
        self.title = title

    def generate(self):
        """Genera el reporte de inventario en PDF"""
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=18,
        )

        elements = []
        elements.extend(self._build_report_content())

        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()

        return pdf

    def _build_report_content(self):
        """Construye el contenido del reporte"""
        elements = []
        styles = getSampleStyleSheet()

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#667eea'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        elements.append(Paragraph(self.title.upper(), title_style))
        elements.append(Paragraph(
            f'Generado el {datetime.now().strftime("%d de %B de %Y a las %H:%M")}',
            ParagraphStyle('Subtitle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10, textColor=colors.grey)
        ))
        elements.append(Spacer(1, 0.3*inch))

        # Create data table
        data = [['Código', 'Nombre', 'Categoría', 'Stock', 'Unidad', 'Costo Unit.', 'Valor Total']]

        total_value = 0
        for item in self.items:
            stock = item.get_total_stock()
            unit_value = float(item.unit_cost)
            total_item_value = stock * unit_value
            total_value += total_item_value

            data.append([
                item.code,
                item.name[:30],  # Truncate long names
                item.get_category_display(),
                f'{stock:.2f}',
                item.get_unit_display(),
                f'${unit_value:,.2f}',
                f'${total_item_value:,.2f}'
            ])

        # Add total row
        data.append(['', '', '', '', '', 'TOTAL:', f'${total_value:,.2f}'])

        # Create table
        table = Table(data, colWidths=[0.8*inch, 2*inch, 1.2*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            # Data rows
            ('ALIGN', (3, 1), (-1, -2), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),

            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), HexColor('#f8f9fa')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, HexColor('#667eea')),
        ]))

        elements.append(table)

        return elements

    def get_response(self):
        """Retorna HttpResponse con el PDF"""
        pdf = self.generate()

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_inventario_{datetime.now().strftime("%Y%m%d")}.pdf"'
        response.write(pdf)

        return response
