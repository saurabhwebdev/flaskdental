from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime
import os

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(id):
    from app.models.user import User
    return User.query.get(int(id))

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dental_clinic.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    migrate = Migrate(app, db)

    with app.app_context():
        # Import models
        from app.models.user import User
        from app.models.patient import Patient
        from app.models.prescription import Prescription, Medication
        from app.models.invoice import Invoice
        from app.models.settings import Settings
        
        # Import routes
        from app.routes import auth, patients, appointments, prescriptions, invoices, settings, main
        
        # Register blueprints
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(patients.bp)
        app.register_blueprint(appointments.bp)
        app.register_blueprint(prescriptions.prescriptions)
        app.register_blueprint(invoices.invoices)
        app.register_blueprint(settings.settings)

        # Create database tables
        db.create_all()

        return app
