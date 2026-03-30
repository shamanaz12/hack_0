# Complete AI Employee Vault System

This project implements a comprehensive automation system with multiple integrated components for task management and email processing.

## System Components

### 1. File Processing Pipeline
- **Drop_Folder**: Entry point for new files/tasks
- **Needs_Action**: Files requiring immediate attention
- **Plans**: Structured plans for each task
- **Pending_Approval**: Items awaiting approval
- **Approved**: Approved plans and decisions
- **Done**: Completed tasks and projects

### 2. Automated File Processing
- **File Watcher**: Monitors Drop_Folder and automatically copies files to Needs_Action
- **Processing System**: Converts files from Needs_Action to structured plans in Plans folder
- **Workflow Management**: Complete workflow from Needs_Action to Done

### 3. Gmail Integration
- **Gmail Poller**: Checks Gmail inbox for new emails
- **Cron Scheduler**: Runs email checks every 5 minutes
- **Markdown Creation**: Automatically creates markdown files from emails in Needs_Action

### 4. MCP Email Server
- **HTTP API**: Send emails via HTTP requests
- **Dry Run Mode**: Test functionality without sending actual emails
- **Secure Credentials**: Uses environment variables for SMTP settings
- **Comprehensive Logging**: Full audit trail of email operations

## Setup Instructions

### Prerequisites
- Python 3.7+
- Required packages (install with `pip install -r requirements.txt`)

### Gmail API Setup
1. Follow the instructions in `GMAIL_SETUP_GUIDE.md`
2. Create a project in Google Cloud Console
3. Enable the Gmail API
4. Create OAuth 2.0 credentials for a desktop application
5. Download the credentials JSON file and rename it to `credentials.json`
6. Place `credentials.json` in the AI_Employee_Vault folder

### Running the System

#### Option 1: Complete System (Recommended)
Run `start_complete_system.bat` to start all components interactively.

#### Option 2: Individual Components
1. **File Watcher**: `python file_watcher.py`
2. **Gmail Cron Scheduler**: `python gmail_cron_scheduler.py`
3. **MCP Email Server**: `python mcp_email_server.py`

#### Option 3: Using Batch Files
- `start_gmail_cron_scheduler.bat` - Starts Gmail checking every 5 minutes
- `start_mcp_server.bat` - Starts the email server
- `start_watcher.bat` - Starts the file watcher

## Environment Variables for MCP Email Server
Set these environment variables before running the MCP server:
- `SMTP_HOST`: SMTP server address
- `SMTP_PORT`: SMTP server port (default: 587)
- `SMTP_USERNAME`: SMTP authentication username
- `SMTP_PASSWORD`: SMTP authentication password
- `SMTP_USE_TLS`: Enable TLS encryption (default: true)

## API Endpoints (MCP Email Server)
- `POST /send-email`: Send an email with JSON payload containing `to`, `subject`, `body`, and optional `dry_run` flag
- `GET /health`: Check server health status

## Security Features
- No hardcoded credentials
- Environment variable-based configuration
- Input sanitization
- Comprehensive logging
- Dry run capabilities for testing

## Logging
- All components maintain detailed logs
- Email server logs to `email_server.log`
- Gmail watcher logs to `gmail_watcher.log`
- Cron scheduler logs to `cron_scheduler.log`

## Troubleshooting
1. If Gmail API doesn't work, ensure `credentials.json` and `token.pickle` exist
2. Check logs for error messages
3. Verify all required dependencies are installed
4. Ensure firewall/antivirus isn't blocking the applications

The system is now fully operational and ready to automate your workflow processes!