from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.invoice import Invoice
from app.models.patient import Patient
from app.models.settings import Settings
from app import db
from datetime import datetime, timedelta

invoices = Blueprint('invoices', __name__, url_prefix='/invoices')

@invoices.route('/')
@login_required
def index():
    invoices = Invoice.query.order_by(Invoice.date.desc()).all()
    settings = Settings.query.first()
    return render_template('invoices/index.html', invoices=invoices, settings=settings)

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
