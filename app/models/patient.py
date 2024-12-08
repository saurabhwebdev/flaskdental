from app import db
from datetime import datetime

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    
    # Medical and Treatment Fields
    chief_complaint = db.Column(db.Text)
    medical_dental_history = db.Column(db.Text)
    on_examination = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment_plan = db.Column(db.Text)
    treatment_done = db.Column(db.Text)
    recall = db.Column(db.Text)
    
    # Timestamps and other fields
    medical_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    prescriptions = db.relationship('Prescription', backref='patient', lazy=True)
    invoices = db.relationship('Invoice', backref='patient', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
