from app import db

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Clinic Information
    clinic_name = db.Column(db.String(100))
    clinic_address = db.Column(db.Text)
    clinic_phone = db.Column(db.String(20))
    clinic_email = db.Column(db.String(100))
    
    # Business Hours - Default 10 AM to 8 PM for weekdays
    hours_monday_start = db.Column(db.String(5), default='10:00')
    hours_monday_end = db.Column(db.String(5), default='20:00')
    hours_monday_closed = db.Column(db.Boolean, default=False)
    
    hours_tuesday_start = db.Column(db.String(5), default='10:00')
    hours_tuesday_end = db.Column(db.String(5), default='20:00')
    hours_tuesday_closed = db.Column(db.Boolean, default=False)
    
    hours_wednesday_start = db.Column(db.String(5), default='10:00')
    hours_wednesday_end = db.Column(db.String(5), default='20:00')
    hours_wednesday_closed = db.Column(db.Boolean, default=False)
    
    hours_thursday_start = db.Column(db.String(5), default='10:00')
    hours_thursday_end = db.Column(db.String(5), default='20:00')
    hours_thursday_closed = db.Column(db.Boolean, default=False)
    
    hours_friday_start = db.Column(db.String(5), default='10:00')
    hours_friday_end = db.Column(db.String(5), default='20:00')
    hours_friday_closed = db.Column(db.Boolean, default=False)
    
    hours_saturday_start = db.Column(db.String(5), default='10:00')
    hours_saturday_end = db.Column(db.String(5), default='20:00')
    hours_saturday_closed = db.Column(db.Boolean, default=True)
    
    hours_sunday_start = db.Column(db.String(5), default='10:00')
    hours_sunday_end = db.Column(db.String(5), default='20:00')
    hours_sunday_closed = db.Column(db.Boolean, default=True)
    
    # Invoice Settings
    invoice_prefix = db.Column(db.String(10), default='INV-')
    default_tax_rate = db.Column(db.Float, default=0.0)
    invoice_footer = db.Column(db.Text)
    currency = db.Column(db.String(3), default='USD')
    currency_symbol = db.Column(db.String(5), default='$')
    
    # Email Settings
    email_appointment_reminders = db.Column(db.Boolean, default=True)
    email_invoice_copy = db.Column(db.Boolean, default=True)
    
    def __init__(self):
        # Set default business hours
        default_hours = {
            'monday': ('10:00', '20:00', False),
            'tuesday': ('10:00', '20:00', False),
            'wednesday': ('10:00', '20:00', False),
            'thursday': ('10:00', '20:00', False),
            'friday': ('10:00', '20:00', False),
            'saturday': ('10:00', '20:00', True),
            'sunday': ('10:00', '20:00', True)
        }
        
        for day, (start, end, closed) in default_hours.items():
            setattr(self, f'hours_{day}_start', start)
            setattr(self, f'hours_{day}_end', end)
            setattr(self, f'hours_{day}_closed', closed)
            
    @property
    def currency_display(self):
        """Return the currency symbol and code"""
        return f"{self.currency_symbol} ({self.currency})"
