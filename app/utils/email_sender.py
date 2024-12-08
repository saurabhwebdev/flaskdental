import os
from datetime import datetime
from flask import render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# HTML template for appointment confirmation
APPOINTMENT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .details { background-color: #f9f9f9; padding: 20px; border-radius: 5px; }
        .footer { margin-top: 30px; text-align: center; font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Appointment Confirmation</h2>
        </div>
        <div class="details">
            <p>Dear {{patient_name}},</p>
            <p>Your appointment has been scheduled at {{clinic_name}}.</p>
            <p><strong>Details:</strong></p>
            <ul>
                <li>Date: {{appointment_date}}</li>
                <li>Time: {{appointment_time}}</li>
                <li>Treatment: {{treatment_type}}</li>
            </ul>
            <p>Location: {{clinic_address}}</p>
            {% if notes %}
            <p><strong>Additional Notes:</strong><br>{{notes}}</p>
            {% endif %}
        </div>
        <div class="footer">
            <p>If you need to reschedule or cancel, please contact us at {{clinic_phone}}</p>
            <p>{{clinic_name}}<br>{{clinic_address}}</p>
        </div>
    </div>
</body>
</html>
"""

def send_appointment_email(appointment, patient, settings):
    """Send appointment confirmation email using Gmail SMTP"""
    try:
        # Get Gmail credentials from environment variables
        gmail_user = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not gmail_user or not gmail_password:
            return False, "Gmail credentials not configured. Please set GMAIL_USER and GMAIL_APP_PASSWORD in .env file"
        
        # Format date and time
        appointment_date = appointment.date.strftime('%B %d, %Y')
        appointment_time = appointment.time.strftime('%I:%M %p')
        
        # Prepare email content
        html_content = render_template_string(
            APPOINTMENT_TEMPLATE,
            patient_name=patient.full_name,
            clinic_name=settings.clinic_name,
            clinic_address=settings.clinic_address,
            clinic_phone=settings.clinic_phone,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            treatment_type=appointment.treatment_type,
            notes=appointment.notes
        )
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Appointment Confirmation - {settings.clinic_name}"
        msg['From'] = gmail_user
        msg['To'] = patient.email
        msg['Reply-To'] = gmail_user
        
        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email using Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_password)
            smtp.send_message(msg)
            
        return True, "Email sent successfully"
        
    except Exception as e:
        return False, str(e)
