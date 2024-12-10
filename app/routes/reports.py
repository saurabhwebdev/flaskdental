from flask import Blueprint, send_file, make_response
from flask_login import login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics import renderPDF
from io import BytesIO
from datetime import datetime, timedelta
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.invoice import Invoice
from app.models.settings import Settings
from app import db
from sqlalchemy import func, and_, extract
import calendar

reports = Blueprint('reports', __name__)

def create_pie_chart(data, labels, title, width=400, height=200):
    drawing = Drawing(width, height)
    
    # Create pie chart
    pie = Pie()
    pie.x = 100
    pie.y = 25
    pie.width = 150
    pie.height = 150
    pie.data = data
    pie.labels = labels
    
    # Add some color and style
    pie.slices.strokeWidth = 0.5
    pie.slices[0].popout = 10
    
    # Use a nice color scheme
    color_scheme = [colors.HexColor('#FF7F11'),  # Primary orange
              colors.HexColor('#4A90E2'),  # Blue
              colors.HexColor('#50C878'),  # Green
              colors.HexColor('#FF6B6B')]  # Red
    
    for i, color in enumerate(color_scheme):
        if i < len(pie.slices):
            pie.slices[i].fillColor = color
    
    # Add title
    title = String(200, 180, title, fontSize=12, textAnchor='middle')
    
    drawing.add(pie)
    drawing.add(title)
    return drawing

def create_bar_chart(data, labels, title, width=400, height=200):
    drawing = Drawing(width, height)
    
    # Create bar chart
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 25
    bc.height = 150
    bc.width = 300
    bc.data = [data]
    bc.strokeColor = colors.black
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = max(data) * 1.2
    bc.valueAxis.valueStep = max(data) * 0.2
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = labels
    
    # Style the bars
    bc.bars[0].fillColor = colors.HexColor('#FF7F11')
    
    # Add title
    title = String(200, 180, title, fontSize=12, textAnchor='middle')
    
    drawing.add(bc)
    drawing.add(title)
    return drawing

@reports.route('/generate_report')
@login_required
def generate_report():
    # Get clinic settings
    settings = Settings.query.first()
    currency_symbol = settings.currency_symbol if settings else '$'
    
    # Create a BytesIO buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object using ReportLab
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#FF7F11')
    )
    
    heading_style = ParagraphStyle(
        'Heading2',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#333333')
    )
    
    subheading_style = ParagraphStyle(
        'Heading3',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=5,
        textColor=colors.HexColor('#666666')
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333')
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Header with clinic information
    header = Drawing(500, 50)
    header.add(String(250, 40, settings.clinic_name if settings else "Dental Clinic Report", fontSize=24, textAnchor='middle', fillColor=colors.HexColor('#FF7F11')))
    header.add(Line(50, 30, 450, 30, strokeColor=colors.HexColor('#FF7F11'), strokeWidth=2))
    elements.append(header)
    
    if settings:
        elements.append(Paragraph(f"Address: {settings.clinic_address}", body_style))
        elements.append(Paragraph(f"Phone: {settings.clinic_phone}", body_style))
        elements.append(Paragraph(f"Email: {settings.clinic_email}", body_style))
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    elements.append(Spacer(1, 30))
    
    # Add decorative line after header
    line = Drawing(500, 1)
    line.add(Line(50, 0, 450, 0, strokeColor=colors.HexColor('#FF7F11'), strokeWidth=1))
    elements.append(line)
    elements.append(Spacer(1, 20))
    
    # Get statistics
    # Overall stats
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    total_invoices = Invoice.query.count()
    total_revenue = db.session.query(func.sum(Invoice.total_amount)).scalar() or 0
    
    # Monthly stats
    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_patients_30d = Patient.query.filter(Patient.created_at >= thirty_days_ago).count()
    appointments_30d = Appointment.query.filter(Appointment.date >= thirty_days_ago).count()
    revenue_30d = db.session.query(func.sum(Invoice.total_amount)).filter(Invoice.date >= thirty_days_ago).scalar() or 0
    
    # Appointment status
    upcoming_appointments = Appointment.query.filter(Appointment.date >= datetime.now()).count()
    completed_appointments = Appointment.query.filter(Appointment.status == 'completed').count()
    cancelled_appointments = Appointment.query.filter(Appointment.status == 'cancelled').count()
    
    # Revenue trends (last 6 months)
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_revenue = []
    month_labels = []
    
    for i in range(5, -1, -1):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        
        revenue = db.session.query(func.sum(Invoice.total_amount))\
            .filter(extract('year', Invoice.date) == year)\
            .filter(extract('month', Invoice.date) == month)\
            .scalar() or 0
        
        monthly_revenue.append(revenue)
        month_labels.append(calendar.month_abbr[month])
    
    # Create charts
    # Appointment Status Pie Chart
    appointment_data = [upcoming_appointments, completed_appointments, cancelled_appointments]
    appointment_labels = ['Upcoming', 'Completed', 'Cancelled']
    appointment_chart = create_pie_chart(appointment_data, appointment_labels, 'Appointment Status Distribution')
    elements.append(appointment_chart)
    elements.append(Spacer(1, 20))
    
    # Monthly Revenue Bar Chart
    revenue_chart = create_bar_chart(monthly_revenue, month_labels, 'Monthly Revenue Trend')
    elements.append(revenue_chart)
    elements.append(Spacer(1, 20))
    
    # Key Performance Indicators
    elements.append(Paragraph("Key Performance Indicators", heading_style))
    
    kpi_data = [
        ['Metric', 'Current', '30-Day Trend'],
        ['Total Patients', str(total_patients), f"+{new_patients_30d}"],
        ['Monthly Revenue', f"{currency_symbol}{monthly_revenue[-1]:,.2f}", 
         f"{'+' if revenue_30d > monthly_revenue[-2] else ''}{currency_symbol}{revenue_30d - monthly_revenue[-2]:,.2f}"],
        ['Avg. Daily Appointments', f"{appointments_30d/30:.1f}", 
         f"{'+' if appointments_30d > total_appointments/180 else ''}{(appointments_30d/30 - total_appointments/180):.1f}"]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[200, 100, 100])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF7F11')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    elements.append(kpi_table)
    elements.append(PageBreak())
    
    # Detailed Statistics
    elements.append(Paragraph("Detailed Analysis", heading_style))
    
    # Financial Metrics
    elements.append(Paragraph("Financial Overview", subheading_style))
    financial_data = [
        ['Metric', 'Value'],
        ['Total Revenue', f"{currency_symbol}{total_revenue:,.2f}"],
        ['Revenue (Last 30 Days)', f"{currency_symbol}{revenue_30d:,.2f}"],
        ['Average Revenue per Patient', f"{currency_symbol}{(total_revenue/total_patients if total_patients > 0 else 0):,.2f}"],
        ['Average Revenue per Appointment', f"{currency_symbol}{(total_revenue/total_appointments if total_appointments > 0 else 0):,.2f}"]
    ]
    
    financial_table = Table(financial_data, colWidths=[200, 200])
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90E2')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    elements.append(financial_table)
    elements.append(Spacer(1, 20))
    
    # Appointment Metrics
    elements.append(Paragraph("Appointment Analytics", subheading_style))
    appointment_data = [
        ['Metric', 'Value'],
        ['Total Appointments', str(total_appointments)],
        ['Upcoming Appointments', str(upcoming_appointments)],
        ['Completed Appointments', str(completed_appointments)],
        ['Cancelled Appointments', str(cancelled_appointments)],
        ['Completion Rate', f"{(completed_appointments/total_appointments*100 if total_appointments > 0 else 0):.1f}%"],
        ['Cancellation Rate', f"{(cancelled_appointments/total_appointments*100 if total_appointments > 0 else 0):.1f}%"]
    ]
    
    appointment_table = Table(appointment_data, colWidths=[200, 200])
    appointment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#50C878')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    elements.append(appointment_table)
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the response
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=dental_clinic_report.pdf'
    
    return response
