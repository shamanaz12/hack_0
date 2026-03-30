#!/usr/bin/env python3
"""Send test email using Python smtplib"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587
email_address = "shama20302022@gmail.com"
email_password = "tnjtsxogdsxhefas"

# Email details
to_email = "shama20302022@gmail.com"
subject = "Test from AI employee"
body = "This is a test email sent from the MCP email server."

try:
    # Create message
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connect and send
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(email_address, email_password)
    server.send_message(msg)
    server.quit()

    print("[OK] Email sent successfully!")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
except Exception as e:
    print(f"Error: {e}")
