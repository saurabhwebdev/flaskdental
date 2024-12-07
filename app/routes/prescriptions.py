from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.prescription import Prescription, Medication
from app.models.patient import Patient
from app.models.settings import Settings
from app import db
from datetime import datetime

prescriptions = Blueprint('prescriptions', __name__)

@prescriptions.route('/prescriptions')
@login_required
def index():
    prescriptions = Prescription.query.order_by(Prescription.date.desc()).all()
    return render_template('prescriptions/index.html', prescriptions=prescriptions)

@prescriptions.route('/prescriptions/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        diagnosis = request.form.get('diagnosis')
        notes = request.form.get('notes')
        
        # Create prescription
        prescription = Prescription(
            patient_id=patient_id,
            date=datetime.now(),
            diagnosis=diagnosis,
            notes=notes
        )
        db.session.add(prescription)
        db.session.flush()  # This gets us the prescription.id
        
        # Get medication details from form
        medication_names = request.form.getlist('medication_name[]')
        medication_dosages = request.form.getlist('medication_dosage[]')
        medication_frequencies = request.form.getlist('medication_frequency[]')
        medication_durations = request.form.getlist('medication_duration[]')
        medication_instructions = request.form.getlist('medication_instructions[]')
        
        # Create medications
        for name, dosage, freq, duration, instr in zip(
            medication_names, medication_dosages, medication_frequencies,
            medication_durations, medication_instructions
        ):
            if name.strip():  # Only add if name is not empty
                medication = Medication(
                    prescription_id=prescription.id,
                    name=name,
                    dosage=dosage,
                    frequency=freq,
                    duration=duration,
                    instructions=instr
                )
                db.session.add(medication)
        
        db.session.commit()
        flash('Prescription created successfully', 'success')
        return redirect(url_for('prescriptions.index'))
    
    patients = Patient.query.all()
    return render_template('prescriptions/new.html', patients=patients)

@prescriptions.route('/prescriptions/<int:id>')
@login_required
def view(id):
    try:
        prescription = Prescription.query.get_or_404(id)
        settings = Settings.query.first()
        if settings is None:
            settings = Settings()  # Create a default settings object if none exists
            db.session.add(settings)
            db.session.commit()
            
        print_mode = request.args.get('print', 'false').lower() == 'true'
        template = 'prescriptions/print.html' if print_mode else 'prescriptions/view.html'
        
        # Ensure we're passing the settings to both templates
        return render_template(
            template,
            prescription=prescription,
            settings=settings,
            print_mode=print_mode
        )
    except Exception as e:
        print(f"Error in prescription view: {str(e)}")  # For debugging
        flash('An error occurred while viewing the prescription', 'error')
        return redirect(url_for('prescriptions.index'))

@prescriptions.route('/prescriptions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    prescription = Prescription.query.get_or_404(id)
    
    if request.method == 'POST':
        prescription.diagnosis = request.form.get('diagnosis')
        prescription.notes = request.form.get('notes')
        
        # Get medication details from form
        medication_names = request.form.getlist('medication_name[]')
        medication_dosages = request.form.getlist('medication_dosage[]')
        medication_frequencies = request.form.getlist('medication_frequency[]')
        medication_durations = request.form.getlist('medication_duration[]')
        medication_instructions = request.form.getlist('medication_instructions[]')
        
        # Remove existing medications
        for medication in prescription.medications:
            db.session.delete(medication)
        
        # Create new medications
        for name, dosage, freq, duration, instr in zip(
            medication_names, medication_dosages, medication_frequencies,
            medication_durations, medication_instructions
        ):
            if name.strip():  # Only add if name is not empty
                medication = Medication(
                    prescription_id=prescription.id,
                    name=name,
                    dosage=dosage,
                    frequency=freq,
                    duration=duration,
                    instructions=instr
                )
                db.session.add(medication)
        
        db.session.commit()
        flash('Prescription updated successfully', 'success')
        return redirect(url_for('prescriptions.view', id=prescription.id))
    
    patients = Patient.query.all()
    return render_template('prescriptions/edit.html', prescription=prescription, patients=patients)

@prescriptions.route('/prescriptions/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    prescription = Prescription.query.get_or_404(id)
    
    try:
        db.session.delete(prescription)
        db.session.commit()
        flash('Prescription deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting prescription: {str(e)}")
        flash(f'Error deleting prescription: {str(e)}', 'error')
    
    return redirect(url_for('prescriptions.index'))
