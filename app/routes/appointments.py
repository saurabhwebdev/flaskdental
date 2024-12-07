from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.models.appointment import Appointment
from app.models.patient import Patient
from app import db
from datetime import datetime

bp = Blueprint('appointments', __name__, url_prefix='/appointments')

@bp.route('/')
@login_required
def index():
    appointments = Appointment.query.order_by(Appointment.date, Appointment.time).all()
    return render_template('appointments/index.html', appointments=appointments)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        try:
            appointment = Appointment(
                patient_id=request.form['patient_id'],
                date=datetime.strptime(request.form['date'], '%Y-%m-%d').date(),
                time=datetime.strptime(request.form['time'], '%H:%M').time(),
                treatment_type=request.form['appointment_type'],
                notes=request.form.get('notes', '')
            )
            db.session.add(appointment)
            db.session.commit()
            flash('Appointment scheduled successfully', 'success')
            return redirect(url_for('appointments.index'))
        except ValueError as e:
            flash('Invalid date or time format', 'error')
        except Exception as e:
            flash('An error occurred while scheduling the appointment', 'error')
    patients = Patient.query.order_by(Patient.last_name).all()
    return render_template('appointments/new.html', patients=patients)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    appointment = Appointment.query.get_or_404(id)
    if request.method == 'POST':
        try:
            appointment.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            appointment.time = datetime.strptime(request.form['time'], '%H:%M').time()
            appointment.treatment_type = request.form['appointment_type']
            appointment.notes = request.form.get('notes', '')
            appointment.status = request.form.get('status', 'scheduled')
            db.session.commit()
            flash('Appointment updated successfully', 'success')
            return redirect(url_for('appointments.index'))
        except ValueError:
            flash('Invalid date or time format', 'error')
        except Exception as e:
            flash('An error occurred while updating the appointment', 'error')
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
        db.session.rollback()
        flash('Error deleting appointment', 'error')
    
    return redirect(url_for('appointments.index'))
