from flask import Blueprint, render_template
from flask_login import login_required
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.invoice import Invoice
from app.models.settings import Settings
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    # Get settings
    settings = Settings.query.first()
    
    # Get today's date
    today = datetime.now().date()
    
    # Get upcoming appointments for the next 7 days
    upcoming_appointments = Appointment.query.filter(
        Appointment.date >= today,
        Appointment.date <= today + timedelta(days=7)
    ).order_by(Appointment.date, Appointment.time).all()
    
    # Get recent patients
    recent_patients = Patient.query.order_by(Patient.created_at.desc()).limit(5).all()
    
    # Get invoice statistics
    total_invoices = Invoice.query.count()
    total_amount = db.session.query(func.sum(Invoice.total_amount)).scalar() or 0
    unpaid_amount = db.session.query(func.sum(Invoice.total_amount - Invoice.paid_amount))\
        .filter(Invoice.status.in_(['unpaid', 'partially_paid'])).scalar() or 0
    overdue_invoices = Invoice.query.filter(
        Invoice.due_date < today,
        Invoice.status.in_(['unpaid', 'partially_paid'])
    ).count()
    
    # Calculate percentage of paid vs unpaid
    total_paid = db.session.query(func.sum(Invoice.paid_amount)).scalar() or 0
    payment_rate = (total_paid / total_amount * 100) if total_amount > 0 else 0
    
    # Get patient statistics
    total_patients = Patient.query.count()
    new_patients_this_month = Patient.query.filter(
        Patient.created_at >= datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    # Get appointment statistics
    total_appointments = Appointment.query.count()
    todays_appointments = Appointment.query.filter(Appointment.date == today).count()
    this_week_appointments = len(upcoming_appointments)
    pending_appointments = Appointment.query.filter(
        Appointment.status == 'scheduled',
        Appointment.date >= today
    ).count()
    
    return render_template('dashboard.html',
                         settings=settings,
                         today=today,
                         upcoming_appointments=upcoming_appointments,
                         recent_patients=recent_patients,
                         total_invoices=total_invoices,
                         total_amount=total_amount,
                         unpaid_amount=unpaid_amount,
                         overdue_invoices=overdue_invoices,
                         payment_rate=payment_rate,
                         total_patients=total_patients,
                         new_patients_this_month=new_patients_this_month,
                         total_appointments=total_appointments,
                         todays_appointments=todays_appointments,
                         this_week_appointments=this_week_appointments,
                         pending_appointments=pending_appointments)
