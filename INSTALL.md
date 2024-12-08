# DentFlow Pro - Installation Guide

Welcome to DentFlow Pro! This guide will help you set up the application on your system. Follow these steps carefully to get started.

## Prerequisites

Before installing DentFlow Pro, make sure you have the following installed on your system:

1. **Python 3.12 or higher**
   - Download from: https://www.python.org/downloads/
   - During installation, make sure to check "Add Python to PATH"

2. **Git** (optional, for cloning the repository)
   - Download from: https://git-scm.com/downloads

## Step-by-Step Installation

### 1. Get the Code

**Option A: Using Git**
```bash
git clone https://github.com/yourusername/FlaskDental.git
cd FlaskDental
```

**Option B: Download ZIP**
- Download the ZIP file from the repository
- Extract it to your desired location
- Open terminal/command prompt and navigate to the extracted folder

### 2. Set Up Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Create a `.env` file in the root directory
2. Add the following configurations:
```env
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///dental.db

# Email Configuration (if using email features)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
```

### 5. Initialize the Database

```bash
# Create database tables
flask db upgrade
```

### 6. Create Admin Account

Create a file named `create_admin.py` in the root directory with the following content:
```python
from app import db, create_app
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_admin_account():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        if not User.query.filter_by(email='admin@dentflow.com').first():
            admin = User(
                first_name='Admin',
                last_name='User',
                email='admin@dentflow.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True,
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin account created successfully!")
            print("Email: admin@dentflow.com")
            print("Password: admin123")
        else:
            print("Admin account already exists!")

if __name__ == '__main__':
    create_admin_account()
```

Then run the script to create the admin account:
```bash
python create_admin.py
```

**Important**: After logging in for the first time, immediately change the default admin password!

### 7. Run the Application

```bash
# Start the development server
flask run
```

The application should now be running at `http://127.0.0.1:5000`

## First-Time Setup

1. Open your web browser and go to `http://127.0.0.1:5000`
2. Log in with your admin credentials
3. Start managing your dental practice!

## Common Issues and Solutions

### Issue 1: "Python not found"
- Make sure Python is properly installed and added to PATH
- Try running `python --version` to verify installation

### Issue 2: "Module not found" errors
- Ensure you've activated the virtual environment
- Try running `pip install -r requirements.txt` again

### Issue 3: Database errors
- Delete the `dental.db` file (if it exists)
- Run `flask db upgrade` again

## Additional Configuration

### Email Setup (Optional)
To enable email notifications:
1. Use a Gmail account
2. Enable 2-factor authentication
3. Generate an App Password
4. Update the `.env` file with your email credentials

### Custom Configurations
- Edit `config.py` for advanced settings
- Modify `instance/config.py` for local overrides

## Support

If you encounter any issues:
1. Check the error logs in the terminal
2. Refer to the common issues section above
3. Create an issue on the GitHub repository
4. Contact support at support@dentflowpro.com

## Security Notes

1. Never share your `.env` file
2. Change the default SECRET_KEY
3. Use strong passwords
4. Regularly update dependencies

## Updating the Application

To update to the latest version:

```bash
# Pull latest changes (if using Git)
git pull origin main

# Install any new dependencies
pip install -r requirements.txt

# Update database
flask db upgrade
```

## Development Setup (For Contributors)

If you want to contribute to the project:

1. Fork the repository
2. Create a new branch for your feature
3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```
4. Run tests:
```bash
pytest
```

## System Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 1GB free space
- **Python**: 3.12 or higher
- **Browser**: Chrome, Firefox, Safari, or Edge (latest versions)

## Creating Desktop Shortcut (Windows Only)

To create a desktop shortcut that automatically starts DentFlow Pro:

1. First, install the required Windows-specific packages:
```bash
pip install pywin32 winshell
```

2. Run the shortcut creation script:
```bash
python run_dentflow.py --create-shortcut
```

3. A "DentFlow Pro" shortcut will be created on your desktop
4. Double-click the shortcut to:
   - Start the Flask server
   - Open your default web browser to the application
   - Show server logs in a console window

**Note**: The shortcut will automatically:
- Activate the virtual environment
- Start the Flask server
- Open your web browser
- Display server logs
- Properly shut down the server when you close the window

To stop the application, simply press Ctrl+C in the console window or close it.
