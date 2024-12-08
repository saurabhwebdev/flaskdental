# DentFlow Pro - Dental Clinic Management System

A comprehensive web-based dental clinic management system built with Flask, offering features for patient management, appointment scheduling, invoicing, and prescription management.

## Features

### 1. Dashboard
- Overview of clinic performance metrics
- Quick access to recent patients and upcoming appointments
- Financial insights including total revenue and pending payments
- Appointment statistics and patient growth metrics

### 2. Patient Management
- Complete patient profiles with medical history
- Contact information and demographic details
- Treatment history tracking
- Patient search and filtering capabilities

### 3. Appointment System
- Interactive appointment scheduling
- Multiple appointment types support
- Status tracking (scheduled, completed, cancelled)
- Calendar view for better scheduling
- Conflict prevention

### 4. Invoicing System
- Professional invoice generation
- Multiple currency support
- Itemized billing
- Tax calculation
- Payment tracking
- Printable invoice format
- Support for partial payments

### 5. Prescription Management
- Digital prescription creation
- Medication details and dosage instructions
- Printable prescription format
- Prescription history tracking

### 6. Settings & Configuration
- Clinic information management
- Business hours configuration
- Currency preferences
- Tax rate settings
- Invoice numbering customization

### 7. Email Integration
- Automatic appointment confirmation emails
- Gmail SMTP integration
- HTML email templates
- Configurable email settings
- Manual email resend functionality
- Error handling and logging

## Technical Details

### Technology Stack
- **Backend Framework**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy
- **Authentication**: Flask-Login
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Form Handling**: Flask-WTF
- **Database Migrations**: Flask-Migrate
- **Email Service**: Gmail SMTP

### Project Structure
```
FlaskDental/
├── app/
│   ├── __init__.py              # Application factory and configuration
│   ├── models/                  # Database models
│   │   ├── appointment.py
│   │   ├── invoice.py
│   │   ├── patient.py
│   │   ├── prescription.py
│   │   ├── settings.py
│   │   └── user.py
│   ├── routes/                  # Route handlers
│   │   ├── appointments.py
│   │   ├── auth.py
│   │   ├── invoices.py
│   │   ├── main.py
│   │   ├── patients.py
│   │   ├── prescriptions.py
│   │   └── settings.py
│   └── templates/               # Jinja2 templates
│       ├── appointments/
│       ├── auth/
│       ├── invoices/
│       ├── patients/
│       ├── prescriptions/
│       ├── settings/
│       ├── base.html
│       └── dashboard.html
├── migrations/                  # Database migrations
├── instance/                    # Instance-specific files
├── .env                        # Environment variables
├── requirements.txt            # Python dependencies
├── run.py                      # Application entry point
├── setup_db.py                # Database setup script
└── create_user.py             # User creation utility

## Installation & Setup

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Git (optional)

### Local Setup Steps

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd FlaskDental
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///instance/dental.db
   GMAIL_USER=your.clinic@gmail.com
   GMAIL_APP_PASSWORD=your-app-password
   ```

5. **Initialize Database**
   ```bash
   flask db upgrade
   python setup_db.py
   ```

6. **Create Admin User**
   ```bash
   python create_user.py
   ```

7. **Run the Application**
   ```bash
   flask run
   ```

   Access the application at `http://localhost:5000`

## Usage Guide

### First-Time Setup
1. Log in with the admin credentials created during setup
2. Go to Settings to configure:
   - Clinic information
   - Business hours
   - Currency preferences
   - Tax rates
   - Invoice settings
   - Email settings

### Daily Operations
1. **Patient Management**
   - Add new patients
   - Update existing patient information
   - View patient history

2. **Appointments**
   - Schedule new appointments
   - Manage existing appointments
   - View daily/weekly schedule

3. **Invoicing**
   - Create new invoices
   - Track payments
   - Generate reports
   - Print invoices

4. **Prescriptions**
   - Create digital prescriptions
   - Print prescriptions
   - View prescription history

5. **Email Management**
   - Configure email settings
   - Send appointment confirmations
   - Resend emails manually

## Customization

### Adding New Features
The modular structure allows easy addition of new features:
1. Create new models in `app/models/`
2. Add corresponding routes in `app/routes/`
3. Create templates in `app/templates/`
4. Update navigation in `base.html`

### Styling
- Tailwind CSS classes can be customized in the HTML templates
- Custom CSS can be added to specific template files

### Business Logic
- Core business logic is in the route handlers
- Model methods handle database operations
- Utility functions can be added to `app/utils/`

## Maintenance

### Database Migrations
When modifying the database schema:
```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

### Backup
Regular backups of the `instance/dental.db` file are recommended.

### Updates
1. Pull latest changes
2. Install any new dependencies
3. Run database migrations
4. Restart the application

## Troubleshooting

### Common Issues
1. **Database Errors**
   - Check database file permissions
   - Ensure all migrations are applied
   - Verify model relationships

2. **Authentication Issues**
   - Clear browser cookies
   - Reset user password using create_user.py
   - Check session configuration

3. **Template Errors**
   - Verify template inheritance
   - Check for missing template files
   - Validate context variables

4. **Email Issues**
   - Check email settings
   - Verify Gmail credentials
   - Check email logs for errors

## Security Considerations

1. **Authentication**
   - Password hashing using Werkzeug
   - Session management with Flask-Login
   - CSRF protection with Flask-WTF

2. **Data Protection**
   - Sensitive data encryption
   - Secure form handling
   - Input validation

3. **Access Control**
   - Role-based access control
   - Route protection with @login_required
   - Session timeout settings

## Future Enhancements

1. **Planned Features**
   - SMS reminders
   - Online appointment booking
   - Patient portal
   - Advanced reporting
   - Inventory management

2. **Technical Improvements**
   - API development
   - Real-time updates
   - Performance optimization
   - Mobile app integration

## Support and Contribution

### Getting Help
- Check the documentation
- Review error logs
- Contact system administrator

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Submit pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
