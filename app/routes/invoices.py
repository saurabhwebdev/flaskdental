from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.invoice import Invoice
from app.models.patient import Patient
from app.models.settings import Settings
from app import db
from datetime import datetime, date, timedelta
from app.utils.pagination import PaginationHelper, SearchHelper, FilterHelper, get_search_args

invoices = Blueprint('invoices', __name__, url_prefix='/invoices')

@invoices.route('/')
@login_required
def index():
    # Get search and filter parameters
    search_term, filters = get_search_args()
    
    # Get pagination parameters
    page, per_page = PaginationHelper.get_page_args()
    
    # Start with base query
    query = Invoice.query.join(Patient)
    
    # Apply search if provided
    search_fields = ['notes', 'Patient.first_name', 'Patient.last_name']
    if search_term:
        search_filters = []
        for field in search_fields:
            if '.' in field:
                model_name, field_name = field.split('.')
                if model_name == 'Patient':
                    search_filters.append(getattr(Patient, field_name).ilike(f'%{search_term}%'))
            else:
                search_filters.append(getattr(Invoice, field).ilike(f'%{search_term}%'))
        if search_filters:
            query = query.filter(db.or_(*search_filters))
    
    # Apply date filter if provided
    date_filter = request.args.get('filter_date')
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            query = query.filter(Invoice.date == filter_date)
        except ValueError:
            flash('Invalid date format', 'error')
    
    # Apply status filter if provided
    status_filter = request.args.get('filter_status')
    if status_filter:
        query = query.filter(Invoice.status == status_filter)
    
    # Order by date and id (which is used to generate invoice number)
    query = query.order_by(Invoice.date.desc(), Invoice.id.desc())
    
    # Paginate results
    pagination = PaginationHelper(Invoice, page, per_page)
    invoices = pagination.paginate_query(query)
    
    # Get current date for template
    current_date = date.today()
    
    settings = Settings.query.first()
    
    return render_template(
        'invoices/index.html',
        invoices=invoices,
        search_term=search_term,
        filters=filters,
        now=current_date,
        settings=settings
    )

@invoices.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    if request.method == 'POST':
        try:
            patient_id = request.form.get('patient_id')
            date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
            due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d')
            notes = request.form.get('notes')
            tax_rate = float(request.form.get('tax_rate', 0))
            
            # Get item details from form
            descriptions = request.form.getlist('item_description[]')
            quantities = request.form.getlist('item_quantity[]')
            prices = request.form.getlist('item_price[]')
            
            if not descriptions or not quantities or not prices:
                flash('Please add at least one item to the invoice', 'error')
                return redirect(url_for('invoices.new'))
            
            # Calculate totals
            items = []
            subtotal = 0
            for desc, qty, price in zip(descriptions, quantities, prices):
                quantity = int(qty)
                unit_price = float(price)
                total = quantity * unit_price
                subtotal += total
                items.append({
                    'description': desc,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total': total
                })
            
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount
            
            # Create invoice
            invoice = Invoice(
                patient_id=patient_id,
                date=date,
                due_date=due_date,
                items=items,
                subtotal=subtotal,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                total_amount=total_amount,
                notes=notes,
                status='unpaid'
            )
            
            db.session.add(invoice)
            db.session.commit()
            
            flash('Invoice created successfully', 'success')
            return redirect(url_for('invoices.view', id=invoice.id))
            
        except ValueError as e:
            flash(f'Error creating invoice: {str(e)}', 'error')
            return redirect(url_for('invoices.new'))
    
    patients = Patient.query.all()
    settings = Settings.query.first()
    today = datetime.now().strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    return render_template('invoices/new.html', patients=patients, today=today, due_date=due_date, settings=settings)

@invoices.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    invoice = Invoice.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Update invoice fields
            invoice.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
            invoice.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
            invoice.status = request.form['status']
            invoice.notes = request.form['notes']
            
            # Handle items and amounts
            descriptions = request.form.getlist('item_description[]')
            quantities = request.form.getlist('item_quantity[]')
            prices = request.form.getlist('item_price[]')
            items = []
            subtotal = 0
            for desc, qty, price in zip(descriptions, quantities, prices):
                quantity = int(qty)
                unit_price = float(price)
                total = quantity * unit_price
                subtotal += total
                items.append({
                    'description': desc,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total': total
                })
            
            tax_rate = float(request.form.get('tax_rate', 0))
            tax_amount = subtotal * (tax_rate / 100)
            total_amount = subtotal + tax_amount
            
            invoice.items = items
            invoice.subtotal = subtotal
            invoice.tax_rate = tax_rate
            invoice.tax_amount = tax_amount
            invoice.total_amount = total_amount
            invoice.paid_amount = float(request.form.get('paid_amount', 0))
            
            db.session.commit()
            flash('Invoice updated successfully', 'success')
            return redirect(url_for('invoices.view', id=invoice.id))
            
        except Exception as e:
            flash('Error updating invoice: ' + str(e), 'error')
            db.session.rollback()
    
    patients = Patient.query.order_by(Patient.first_name).all()
    settings = Settings.query.first()
    return render_template('invoices/edit.html', invoice=invoice, patients=patients, settings=settings)

@invoices.route('/<int:id>')
@login_required
def view(id):
    invoice = Invoice.query.get_or_404(id)
    settings = Settings.query.first()
    print_mode = request.args.get('print', False)
    template = 'invoices/print.html' if print_mode else 'invoices/view.html'
    return render_template(template, invoice=invoice, settings=settings)

@invoices.route('/<int:id>/status', methods=['POST'])
@login_required
def update_status(id):
    invoice = Invoice.query.get_or_404(id)
    status = request.form.get('status')
    paid_amount = float(request.form.get('paid_amount', 0))
    
    if status not in ['paid', 'partially_paid', 'unpaid']:
        flash('Invalid status', 'error')
        return redirect(url_for('invoices.view', id=id))
    
    if status == 'paid':
        paid_amount = invoice.total_amount
    elif status == 'unpaid':
        paid_amount = 0
    
    if paid_amount > invoice.total_amount:
        flash('Paid amount cannot be greater than total amount', 'error')
        return redirect(url_for('invoices.view', id=id))
    
    invoice.status = status
    invoice.paid_amount = paid_amount
    
    if paid_amount == invoice.total_amount:
        invoice.status = 'paid'
    elif paid_amount > 0:
        invoice.status = 'partially_paid'
    else:
        invoice.status = 'unpaid'
    
    db.session.commit()
    
    flash('Invoice status updated successfully', 'success')
    return redirect(url_for('invoices.view', id=id))

@invoices.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    invoice = Invoice.query.get_or_404(id)
    
    try:
        db.session.delete(invoice)
        db.session.commit()
        flash('Invoice deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting invoice', 'error')
    
    return redirect(url_for('invoices.index'))
