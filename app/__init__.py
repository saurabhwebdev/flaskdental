from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    
    # Set up the SQLite database path
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(os.path.dirname(basedir), 'instance', 'dental_clinic.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
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
        from app.models.appointment import Appointment
        
        # Import routes
        from app.routes import auth, patients, appointments, prescriptions, invoices, settings, main, reports
        
        # Register blueprints
        app.register_blueprint(auth.bp)
        app.register_blueprint(patients.bp)
        app.register_blueprint(appointments.bp)
        app.register_blueprint(prescriptions.prescriptions)
        app.register_blueprint(invoices.invoices)
        app.register_blueprint(settings.settings)
        app.register_blueprint(main.bp)
        app.register_blueprint(reports.reports)

        # Register template helpers
        from app.utils.template_helpers import update_url_query
        app.jinja_env.globals.update(update_url_query=update_url_query)

        # Create database tables
        db.create_all()
        
        return app
