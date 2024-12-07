from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.models.patient import Patient
from app import db
from datetime import datetime

bp = Blueprint('patients', __name__, url_prefix='/patients')

@bp.route('/')
@login_required
def index():
    patients = Patient.query.order_by(Patient.last_name).all()
    return render_template('patients/index.html', patients=patients)

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        try:
            # Convert date string to Python date object
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            
            patient = Patient(
                first_name=request.form['first_name'],
                last_name=request.form['last_name'],
                date_of_birth=date_of_birth,
                gender=request.form['gender'],
                phone=request.form['phone'],
                email=request.form['email'],
                address=request.form['address'],
                medical_history=request.form['medical_history']
            )
            db.session.add(patient)
            db.session.commit()
            flash('Patient added successfully', 'success')
            return redirect(url_for('patients.index'))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
            return render_template('patients/new.html')
        except Exception as e:
            flash('An error occurred while adding the patient.', 'error')
            return render_template('patients/new.html')
    return render_template('patients/new.html')

@bp.route('/<int:id>')
@login_required
def view(id):
    patient = Patient.query.get_or_404(id)
    return render_template('patients/view.html', patient=patient)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Convert date string to Python date object
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            
            patient.first_name = request.form['first_name']
            patient.last_name = request.form['last_name']
            patient.date_of_birth = date_of_birth
            patient.gender = request.form['gender']
            patient.phone = request.form['phone']
            patient.email = request.form['email']
            patient.address = request.form['address']
            patient.medical_history = request.form['medical_history']
            
            db.session.commit()
            flash('Patient updated successfully', 'success')
            return redirect(url_for('patients.view', id=patient.id))
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
        except Exception as e:
            flash('An error occurred while updating the patient.', 'error')
    return render_template('patients/edit.html', patient=patient)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    patient = Patient.query.get_or_404(id)
    
    try:
        # Check for related records
        if patient.appointments or patient.prescriptions or patient.invoices:
            flash('Cannot delete patient with existing appointments, prescriptions, or invoices.', 'error')
            return redirect(url_for('patients.view', id=id))
            
        db.session.delete(patient)
        db.session.commit()
        flash('Patient deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting patient', 'error')
    
    return redirect(url_for('patients.index'))
