import os
from datetime import datetime
from flask import render_template_string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_appointment_email_template(appointment, patient, settings):
    """Generate a modern and attractive HTML email template for appointment confirmation."""
    appointment_date = appointment.date.strftime('%B %d, %Y')  # e.g., December 8, 2024
    appointment_time = appointment.time.strftime('%I:%M %p')   # e.g., 02:30 PM
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 40px 20px;
            }}
            .header {{
                text-align: center;
                padding-bottom: 30px;
                border-bottom: 2px solid #f0f0f0;
                margin-bottom: 30px;
            }}
            .clinic-name {{
                color: #2563eb;
                font-size: 28px;
                font-weight: 700;
                margin: 0;
            }}
            .confirmation-box {{
                background-color: #f8fafc;
                border-radius: 12px;
                padding: 30px;
                margin: 25px 0;
                border: 1px solid #e2e8f0;
            }}
            .appointment-details {{
                margin: 20px 0;
            }}
            .detail-row {{
                display: block;
                margin: 12px 0;
            }}
            .label {{
                color: #64748b;
                font-size: 14px;
                font-weight: 500;
            }}
            .value {{
                color: #1e293b;
                font-size: 16px;
                font-weight: 600;
            }}
            .footer {{
                text-align: center;
                color: #64748b;
                font-size: 14px;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #f0f0f0;
            }}
            .contact-info {{
                margin-top: 25px;
                text-align: center;
            }}
            .contact-info p {{
                margin: 5px 0;
                color: #64748b;
                font-size: 14px;
            }}
            .highlight {{
                color: #2563eb;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="clinic-name">{settings.clinic_name}</h1>
            </div>
            
            <p>Dear {patient.first_name},</p>
            
            <p>Your dental appointment has been confirmed. Here are your appointment details:</p>
            
            <div class="confirmation-box">
                <div class="appointment-details">
                    <div class="detail-row">
                        <span class="label">Date:</span><br>
                        <span class="value">{appointment_date}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Time:</span><br>
                        <span class="value">{appointment_time}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Treatment:</span><br>
                        <span class="value">{appointment.treatment_type}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Duration:</span><br>
                        <span class="value">{appointment.duration} minutes</span>
                    </div>
                </div>
            </div>

            <p>Please arrive <span class="highlight">10 minutes</span> before your appointment time. If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
            
            <div class="contact-info">
                <p>{settings.clinic_address}</p>
                <p>Phone: {settings.clinic_phone}</p>
                <p>Email: {settings.clinic_email}</p>
            </div>
            
            <div class="footer">
                <p>Thank you for choosing {settings.clinic_name}!</p>
                <p>This is an automated message, please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def send_appointment_email(appointment, patient, settings):
    """Send appointment confirmation email using Gmail SMTP"""
    try:
        # Get Gmail credentials from environment variables
        gmail_user = os.getenv('GMAIL_USER')
        gmail_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not gmail_user or not gmail_password:
            return False, "Gmail credentials not configured. Please set GMAIL_USER and GMAIL_APP_PASSWORD in .env file"
        
        # Prepare email content
        html_content = get_appointment_email_template(appointment, patient, settings)
        
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
