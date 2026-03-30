# MCP Email Server

A minimal server for sending emails via Model Context Protocol (MCP).

## Features

- Send emails with `to`, `subject`, and `body` parameters
- Dry run mode for testing without sending actual emails
- Comprehensive logging
- Secure credential handling via environment variables
- Input validation and sanitization

## Prerequisites

- Python 3.7+
- pip

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements_mcp.txt
   ```

2. Set environment variables:
   ```bash
   export SMTP_HOST=your-smtp-server.com
   export SMTP_PORT=587
   export SMTP_USERNAME=your-username
   export SMTP_PASSWORD=your-password
   export SMTP_USE_TLS=true
   ```

## Usage

Start the server:
```bash
python mcp_email_server.py
```

The server will start on `http://localhost:5000`.

## API Endpoints

### POST /send-email
Send an email.

Request body:
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body content...",
  "dry_run": false
}
```

Response:
```json
{
  "status": "success",
  "message": "Email sent successfully",
  "dry_run": false
}
```

### GET /health
Check server health.

Response:
```json
{
  "status": "healthy",
  "timestamp": "2023-01-01T00:00:00.000000",
  "features": ["email_sending", "dry_run", "logging"]
}
```

## Environment Variables

- `SMTP_HOST`: SMTP server address (required)
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USERNAME`: SMTP authentication username (required)
- `SMTP_PASSWORD`: SMTP authentication password (required)
- `SMTP_USE_TLS`: Enable TLS encryption (default: true)

## Security

- Credentials are loaded from environment variables, never hardcoded
- Input is sanitized to prevent injection attacks
- All email attempts are logged for audit purposes
- Dry run mode allows testing without sending actual emails