"""
Minimal MCP Server for Sending Emails

Features:
- Input: to, subject, body
- Dry run mode
- Logging
- No hardcoded credentials
- Use environment variables
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import Flask, request, jsonify
from functools import wraps


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MCPEmailServer:
    def __init__(self):
        # Load SMTP credentials from environment variables
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.use_tls = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
        
        # Validate required environment variables
        if not all([self.smtp_host, self.smtp_port, self.smtp_username, self.smtp_password]):
            raise ValueError("Missing required environment variables for SMTP configuration")
    
    def validate_email_request(self, data):
        """Validate email request parameters"""
        required_fields = ['to', 'subject', 'body']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Basic validation for email format
        if '@' not in data['to']:
            raise ValueError("Invalid email address format")
        
        return True
    
    def sanitize_input(self, data):
        """Sanitize input to prevent injection attacks"""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Remove potentially dangerous characters
                sanitized[key] = value.replace('\r\n', '').replace('\n', '')
            else:
                sanitized[key] = value
        return sanitized
    
    def send_email(self, to, subject, body, dry_run=False):
        """Send email via SMTP"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to
            msg['Subject'] = subject
            
            # Add body to email
            msg.attach(MIMEText(body, 'plain'))
            
            if dry_run:
                logger.info(f"Dry run: Would send email to {to} with subject '{subject}'")
                logger.info(f"Dry run: Body preview: {body[:100]}...")
                return {"status": "success", "message": "Dry run completed", "dry_run": True}
            
            # Connect to server and send email
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            if self.use_tls:
                server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            
            text = msg.as_string()
            server.sendmail(self.smtp_username, to, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to}")
            return {"status": "success", "message": "Email sent successfully", "dry_run": False}
            
        except Exception as e:
            error_msg = f"Failed to send email to {to}: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg, "dry_run": dry_run}


# Initialize Flask app
app = Flask(__name__)
email_server = MCPEmailServer()


def require_json(f):
    """Decorator to ensure request contains JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        return f(*args, **kwargs)
    return decorated_function


@app.route('/send-email', methods=['POST'])
@require_json
def send_email_endpoint():
    """MCP endpoint for sending emails"""
    try:
        data = request.get_json()
        
        # Check for dry run mode
        dry_run = data.get('dry_run', False)
        
        # Validate request
        email_server.validate_email_request(data)
        
        # Sanitize inputs
        sanitized_data = email_server.sanitize_input(data)
        
        # Extract parameters
        to = sanitized_data['to']
        subject = sanitized_data['subject']
        body = sanitized_data['body']
        
        # Send email
        result = email_server.send_email(to, subject, body, dry_run=dry_run)
        
        return jsonify(result), 200 if result['status'] == 'success' else 500
        
    except ValueError as ve:
        logger.warning(f"Validation error: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "features": ["email_sending", "dry_run", "logging"]
    }), 200


if __name__ == '__main__':
    print("Starting MCP Email Server...")
    print(f"SMTP Host: {email_server.smtp_host}")
    print(f"SMTP Port: {email_server.smtp_port}")
    print(f"TLS Enabled: {email_server.use_tls}")
    print("Server is running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)