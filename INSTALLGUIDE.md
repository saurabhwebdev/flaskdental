# DentFlow Pro Installation Guide

Welcome to DentFlow Pro - Your Local-First Dental Practice Management Solution! 

## Why DentFlow Pro?

DentFlow Pro is designed with your privacy in mind. Unlike cloud-based solutions:
- All data stays on your computer
- No internet connection required
- Complete control over your data
- Enhanced privacy and security

## System Requirements

Before installing, ensure your system meets these requirements:

### Hardware Requirements
- Windows 10/11 (64-bit)
- 4GB RAM (minimum)
- 500MB free disk space
- 1280x720 minimum screen resolution

### Software Requirements
- Python 3.12 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, or Edge)

## Step-by-Step Installation

### 1. Install Python
1. Visit [python.org](https://www.python.org/downloads/)
2. Download Python 3.12 for Windows
3. Run the installer
4. **IMPORTANT**: Check "Add Python to PATH"
5. Click "Install Now"
6. Verify installation by opening Command Prompt:
   ```cmd
   python --version
   ```
   Should show Python 3.12.x

### 2. Download DentFlow Pro
1. Download the latest release
2. Create a folder (e.g., `C:\DentFlowPro`)
3. Extract the ZIP file to this folder

### 3. Set Up Python Environment
1. Open Command Prompt as Administrator
2. Navigate to your DentFlow Pro folder:
   ```cmd
   cd C:\DentFlowPro
   ```
3. Create a virtual environment:
   ```cmd
   python -m venv venv
   ```
4. Activate the environment:
   ```cmd
   venv\Scripts\activate
   ```
   Your prompt should now show `(venv)`

### 4. Install Required Packages
1. Ensure you're in the virtual environment
2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
   This may take a few minutes.

### 5. Configure the Application
1. Create a `.env` file in the root directory
2. Add these settings:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secure-secret-key
   DATABASE_URL=sqlite:///instance/dentflow.db

   # Email Settings (Gmail)
   GMAIL_USER=your.clinic@gmail.com
   GMAIL_APP_PASSWORD=your-app-password-here
   ```

### 6. Initialize the Database
1. Run the setup script:
   ```cmd
   python init_db.py
   ```
2. Create an admin user:
   ```cmd
   python create_user.py
   ```
   Follow the prompts to create your admin account

### 7. Start DentFlow Pro
1. Run the application:
   ```cmd
   python run.py
   ```
2. Open your browser and go to:
   ```
   http://localhost:5000
   ```
3. Log in with your admin credentials

## Email Configuration
To enable email functionality, you need to:
1. Have a Gmail account for your clinic
2. Enable 2-Step Verification in your Google Account:
   - Go to Google Account Settings
   - Security → 2-Step Verification → Turn it on
3. Generate an App Password:
   - Go to Google Account Settings
   - Security → App passwords
   - Select app: Mail
   - Select device: Other (Custom name)
   - Enter "DentFlow Pro"
   - Copy the generated 16-character password
4. Update your `.env` file with:
   - `GMAIL_USER`: Your clinic's Gmail address
   - `GMAIL_APP_PASSWORD`: The 16-character app password

## First-Time Setup

After installation, complete these steps:

1. **Change Default Password**
   - Go to Settings
   - Update your password
   - Never share your admin credentials

2. **Configure Clinic Details**
   - Add your clinic information
   - Set business hours
   - Configure regional settings

3. **Test Core Features**
   - Create a test patient
   - Schedule a test appointment
   - Generate a test prescription

## Data Storage

Your data is stored locally in these locations:

```
C:\DentFlowPro\
├── instance\
│   ├── dentflow.db         # Main database
│   ├── records\            # Patient records
│   └── backups\            # Automatic backups
```

## Backup Your Data

We recommend regular backups:

1. Automatic Backups
   - Located in `instance/backups`
   - Created daily
   - Encrypted for security

2. Manual Backup
   ```cmd
   python backup.py
   ```

## Troubleshooting

### Common Issues

1. **"Python not found"**
   - Reinstall Python
   - Ensure "Add to PATH" was checked
   - Restart Command Prompt

2. **"Port already in use"**
   - Change port in config.py
   - Close other applications using port 5000

3. **Database Errors**
   - Ensure write permissions
   - Check disk space
   - Verify SQLite installation

### Email Issues
1. **Emails not sending:**
   - Check Gmail credentials in `.env` file
   - Ensure 2-Step Verification is enabled
   - Verify App Password is correct
   - Check patient has valid email address

2. **Gmail security:**
   - If you get security alerts from Google:
     1. Go to Google Account → Security
     2. Verify the login attempt was from your application
     3. Allow access if prompted

3. **App Password not working:**
   - Delete existing app password
   - Generate a new one
   - Update `.env` file with new password

### Getting Help

If you encounter issues:
1. Check `logs/dentflow.log`
2. Verify all installation steps
3. Ensure system requirements are met

## Security Best Practices

1. **System Security**
   - Keep Windows updated
   - Use antivirus software
   - Enable Windows Defender

2. **Application Security**
   - Change default passwords
   - Regular backups
   - Limit admin access

3. **Data Protection**
   - Regular system backups
   - Secure computer access
   - Use strong passwords

## Updating DentFlow Pro

To update to a new version:

1. Backup your data
2. Download the new release
3. Extract to a new folder
4. Copy your `instance` folder
5. Follow installation steps 3-7

## Need Help?

- Check our documentation
- Review error logs
- Contact support

---

Remember: Your data stays on your computer - DentFlow Pro is designed to protect your privacy and give you complete control over your dental practice data.
