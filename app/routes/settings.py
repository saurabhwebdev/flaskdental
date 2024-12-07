from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.settings import Settings
from app import db

settings = Blueprint('settings', __name__)

CURRENCY_CHOICES = [
    ('USD', '$', 'US Dollar'),
    ('EUR', '€', 'Euro'),
    ('GBP', '£', 'British Pound'),
    ('INR', '₹', 'Indian Rupee'),
    ('JPY', '¥', 'Japanese Yen'),
    ('AUD', 'A$', 'Australian Dollar'),
    ('CAD', 'C$', 'Canadian Dollar')
]

@settings.route('/settings', methods=['GET', 'POST'])
@login_required
def index():
    # Get current settings or create new if not exists
    settings_obj = Settings.query.first()
    if not settings_obj:
        settings_obj = Settings()
        db.session.add(settings_obj)
        db.session.commit()
    
    if request.method == 'POST':
        try:
            # Update clinic information
            settings_obj.clinic_name = request.form.get('clinic_name')
            settings_obj.clinic_address = request.form.get('clinic_address')
            settings_obj.clinic_phone = request.form.get('clinic_phone')
            settings_obj.clinic_email = request.form.get('clinic_email')
            
            # Update business hours
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                setattr(settings_obj, f'hours_{day}_start', request.form.get(f'hours_{day}_start'))
                setattr(settings_obj, f'hours_{day}_end', request.form.get(f'hours_{day}_end'))
                setattr(settings_obj, f'hours_{day}_closed', f'hours_{day}_closed' in request.form)
            
            # Update invoice settings
            settings_obj.invoice_prefix = request.form.get('invoice_prefix')
            settings_obj.default_tax_rate = float(request.form.get('default_tax_rate', 0))
            settings_obj.invoice_footer = request.form.get('invoice_footer')
            
            # Update currency settings
            selected_currency = request.form.get('currency', 'USD')
            for currency_code, symbol, name in CURRENCY_CHOICES:
                if currency_code == selected_currency:
                    settings_obj.currency = currency_code
                    settings_obj.currency_symbol = symbol
                    break
            
            # Update email settings
            settings_obj.email_appointment_reminders = 'email_appointment_reminders' in request.form
            settings_obj.email_invoice_copy = 'email_invoice_copy' in request.form
            
            db.session.commit()
            flash('Settings updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating settings: {str(e)}', 'error')
        
        return redirect(url_for('settings.index'))
    
    return render_template('settings/index.html', settings=settings_obj, currencies=CURRENCY_CHOICES)
