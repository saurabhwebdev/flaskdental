from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required
from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.settings import Settings
from app.utils.email_sender import send_appointment_email
from app.utils.pagination import PaginationHelper, SearchHelper, FilterHelper, get_search_args
from app import db
from datetime import datetime, date
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@bp.route('/')
@login_required
def index():
    # Get search and filter parameters
    search_term, filters = get_search_args()
    
    # Get pagination parameters
    page, per_page = PaginationHelper.get_page_args()
    
    # Start with base query
    query = Appointment.query.join(Patient)
    
    # Apply search if provided
    search_fields = ['treatment_type', 'notes', 'Patient.first_name', 'Patient.last_name']
    if search_term:
        search_filters = []
        for field in search_fields:
            if '.' in field:
                model_name, field_name = field.split('.')
                if model_name == 'Patient':
                    search_filters.append(getattr(Patient, field_name).ilike(f'%{search_term}%'))
            else:
                search_filters.append(getattr(Appointment, field).ilike(f'%{search_term}%'))
        if search_filters:
            query = query.filter(db.or_(*search_filters))
    
    # Apply date filter if provided
    date_filter = request.args.get('filter_date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(Appointment.date == filter_date)
        except ValueError:
            flash('Invalid date format', 'error')
    
    # Apply status filter if provided
    status_filter = request.args.get('filter_status')
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    # Order by date and time
    query = query.order_by(Appointment.date.desc(), Appointment.time.asc())
    
    # Paginate results
    pagination = PaginationHelper(Appointment, page, per_page)
    appointments = pagination.paginate_query(query)
    
    # Get current date for template
    current_date = date.today()
    
    return render_template(
        'appointments/index.html',
        appointments=appointments,
        search_term=search_term,
        filters=filters,
        now=current_date
    )

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        try:
            # Get form data
            patient_id = request.form.get('patient_id')
            date_str = request.form.get('date')
            time_str = request.form.get('time')
            treatment_type = request.form.get('treatment_type')
            duration = request.form.get('duration')
            notes = request.form.get('notes', '')

            # Validate required fields
            if not all([patient_id, date_str, time_str, treatment_type, duration]):
                flash('Please fill in all required fields', 'error')
                patients = Patient.query.order_by(Patient.last_name).all()
                return render_template('appointments/new.html', patients=patients)

            # Convert date and time strings to Python objects
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            time = datetime.strptime(time_str, '%H:%M').time()
            
            # Create appointment
            appointment = Appointment(
                patient_id=patient_id,
                date=date,
                time=time,
                duration=int(duration),
                treatment_type=treatment_type,
                notes=notes,
                status='scheduled'
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            # Get patient and settings
            patient = Patient.query.get(appointment.patient_id)
            settings = Settings.query.first()
            
            if not settings:
                settings = Settings(
                    clinic_name="Dental Clinic",
                    email_appointment_reminders=True
                )
                db.session.add(settings)
                db.session.commit()
            
            # Log debug information
            logger.info(f"Patient email: {patient.email}")
            logger.info(f"Settings: {settings.email_appointment_reminders}")
            
            # Send confirmation email if patient has email
            if patient.email:
                logger.info("Patient has email, attempting to send...")
                try:
                    success, message = send_appointment_email(appointment, patient, settings)
                    logger.info(f"Email send attempt result: {success}, {message}")
                    if success:
                        flash('Appointment created and confirmation email sent', 'success')
                    else:
                        flash(f'Appointment created but email failed: {message}', 'warning')
                except Exception as e:
                    logger.error(f"Email send error: {str(e)}")
                    flash(f'Appointment created but email failed: {str(e)}', 'warning')
            else:
                logger.info("Patient has no email, skipping email send")
                flash('Appointment created successfully (no email address provided)', 'success')
            
            return redirect(url_for('appointments.index'))
            
        except ValueError as e:
            logger.error(f"Value error: {str(e)}")
            flash(f'Invalid date or time format: {str(e)}', 'error')
            patients = Patient.query.order_by(Patient.last_name).all()
            return render_template('appointments/new.html', patients=patients)
        except Exception as e:
            logger.error(f"General error: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'error')
            patients = Patient.query.order_by(Patient.last_name).all()
            return render_template('appointments/new.html', patients=patients)
    
    patients = Patient.query.order_by(Patient.last_name).all()
    return render_template('appointments/new.html', patients=patients)

@bp.route('/<int:id>/resend-email')
@login_required
def resend_email(id):
    try:
        appointment = Appointment.query.get_or_404(id)
        patient = Patient.query.get(appointment.patient_id)
        settings = Settings.query.first()
        
        if not patient.email:
            return jsonify({'success': False, 'message': 'Patient has no email address'}), 400
            
        if not settings:
            return jsonify({'success': False, 'message': 'Clinic settings not configured'}), 400
        
        success, message = send_appointment_email(appointment, patient, settings)
        
        if success:
            return jsonify({'success': True, 'message': 'Confirmation email resent successfully'})
        else:
            return jsonify({'success': False, 'message': f'Failed to send email: {message}'}), 500
            
    except Exception as e:
        logger.error(f"Resend email error: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    appointment = Appointment.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            appointment.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            appointment.time = datetime.strptime(request.form['time'], '%H:%M').time()
            appointment.treatment_type = request.form['treatment_type']
            appointment.duration = int(request.form['duration'])
            appointment.status = request.form['status']
            appointment.notes = request.form.get('notes', '')
            
            db.session.commit()
            flash('Appointment updated successfully', 'success')
            return redirect(url_for('appointments.index'))
        except ValueError as e:
            logger.error(f"Value error in edit appointment: {str(e)}")
            flash('Invalid date or time format', 'error')
        except Exception as e:
            logger.error(f"Error editing appointment: {str(e)}")
            flash(f'An error occurred: {str(e)}', 'error')
    
    patients = Patient.query.order_by(Patient.last_name).all()
    return render_template('appointments/edit.html', appointment=appointment, patients=patients)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    appointment = Appointment.query.get_or_404(id)
    try:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment deleted successfully', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    return redirect(url_for('appointments.index'))
