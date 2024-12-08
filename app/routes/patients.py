from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.models.patient import Patient
from app import db
from datetime import datetime, date
from app.utils.pagination import PaginationHelper, SearchHelper, FilterHelper, get_search_args

bp = Blueprint('patients', __name__, url_prefix='/patients')

@bp.route('/')
@login_required
def index():
    # Get search and filter parameters
    search_term, filters = get_search_args()
    
    # Get pagination parameters
    page, per_page = PaginationHelper.get_page_args()
    
    # Start with base query
    query = Patient.query
    
    # Apply search if provided
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    query = SearchHelper.apply_search(query, Patient, search_term, search_fields)
    
    # Apply filters if provided
    query = FilterHelper.apply_filters(query, Patient, filters)
    
    # Order by name
    query = query.order_by(Patient.last_name, Patient.first_name)
    
    # Paginate results
    pagination = PaginationHelper(Patient, page, per_page)
    patients = pagination.paginate_query(query)
    
    # Get current date for age calculation
    current_date = date.today()
    
    return render_template(
        'patients/index.html',
        patients=patients,
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
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
            gender = request.form.get('gender')
            phone = request.form.get('phone')
            email = request.form.get('email')
            address = request.form.get('address')
            
            # Get medical and treatment information
            chief_complaint = request.form.get('chief_complaint')
            medical_dental_history = request.form.get('medical_dental_history')
            on_examination = request.form.get('on_examination')
            diagnosis = request.form.get('diagnosis')
            treatment_plan = request.form.get('treatment_plan')
            treatment_done = request.form.get('treatment_done')
            recall = request.form.get('recall')
            
            # Create new patient
            patient = Patient(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth,
                gender=gender,
                phone=phone,
                email=email,
                address=address,
                chief_complaint=chief_complaint,
                medical_dental_history=medical_dental_history,
                on_examination=on_examination,
                diagnosis=diagnosis,
                treatment_plan=treatment_plan,
                treatment_done=treatment_done,
                recall=recall
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
    current_date = date.today()
    if request.args.get('print') == 'true':
        return render_template('patients/print.html', 
                             patient=patient, 
                             now=current_date,
                             first_name=patient.first_name,
                             last_name=patient.last_name,
                             date_of_birth=patient.date_of_birth,
                             gender=patient.gender,
                             phone=patient.phone,
                             email=patient.email,
                             address=patient.address,
                             chief_complaint=patient.chief_complaint,
                             medical_dental_history=patient.medical_dental_history,
                             on_examination=patient.on_examination,
                             diagnosis=patient.diagnosis,
                             treatment_plan=patient.treatment_plan,
                             treatment_done=patient.treatment_done,
                             recall=patient.recall)
    return render_template('patients/view.html', 
                         patient=patient, 
                         now=current_date,
                         first_name=patient.first_name,
                         last_name=patient.last_name,
                         date_of_birth=patient.date_of_birth,
                         gender=patient.gender,
                         phone=patient.phone,
                         email=patient.email,
                         address=patient.address,
                         chief_complaint=patient.chief_complaint,
                         medical_dental_history=patient.medical_dental_history,
                         on_examination=patient.on_examination,
                         diagnosis=patient.diagnosis,
                         treatment_plan=patient.treatment_plan,
                         treatment_done=patient.treatment_done,
                         recall=patient.recall)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
            gender = request.form.get('gender')
            phone = request.form.get('phone')
            email = request.form.get('email')
            address = request.form.get('address')
            
            # Get medical and treatment information
            chief_complaint = request.form.get('chief_complaint')
            medical_dental_history = request.form.get('medical_dental_history')
            on_examination = request.form.get('on_examination')
            diagnosis = request.form.get('diagnosis')
            treatment_plan = request.form.get('treatment_plan')
            treatment_done = request.form.get('treatment_done')
            recall = request.form.get('recall')
            
            # Update patient
            patient.first_name = first_name
            patient.last_name = last_name
            patient.date_of_birth = date_of_birth
            patient.gender = gender
            patient.phone = phone
            patient.email = email
            patient.address = address
            patient.chief_complaint = chief_complaint
            patient.medical_dental_history = medical_dental_history
            patient.on_examination = on_examination
            patient.diagnosis = diagnosis
            patient.treatment_plan = treatment_plan
            patient.treatment_done = treatment_done
            patient.recall = recall
            
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
