# MCP Email Server - Send Emails via Model Context Protocol

## Overview

This MCP (Model Context Protocol) server exposes email sending capabilities to AI assistants via the `send_email` tool.

### Components

| File | Purpose |
|------|---------|
| `email_mcp.js` | Node.js MCP email server |
| `mcp_email_server.py` | Python MCP email server |
| `mcp_email_client.py` | Python client library |
| `orchestrator.py` | Integrated with Approved folder |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                             │
│                                                             │
│  Watches: Approved/ folder                                  │
│    │                                                          │
│    ▼                                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  File moved to Approved/                            │   │
│  │    │                                                  │   │
│  │    ▼                                                  │   │
│  │  MCP Email Client                                    │   │
│  │    │                                                  │   │
│  │    ▼                                                  │   │
│  │  MCP Email Server (stdio)                            │   │
│  │    │                                                  │   │
│  │    ▼                                                  │   │
│  │  SMTP/Gmail API                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Result: Email sent → File moved to Done/                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Option 1: Node.js Version (Recommended)

```bash
# Install dependencies
npm install @modelcontextprotocol/sdk nodemailer

# Configure email
node email_mcp.js --email your@email.com --password app-password --save-config

# Run server
node email_mcp.js
```

### Option 2: Python Version

```bash
# Install dependencies
pip install mcp

# Configure email
python mcp_email_server.py --email your@email.com --password app-password --save-config

# Run server
python mcp_email_server.py
```

---

## Configuration

### Config File Location

- **Windows:** `%APPDATA%\qwen-code\email_config.json`
- **Linux/Mac:** `~/.config/qwen-code/email_config.json`

### Config Format

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "email": "your@gmail.com",
  "app_password": "your-app-password"
}
```

### Environment Variables

```bash
set EMAIL_ADDRESS=your@gmail.com
set EMAIL_PASSWORD=your-app-password
set SMTP_SERVER=smtp.gmail.com
set SMTP_PORT=587
```

---

## Gmail App Password Setup

1. Go to [Google Account](https://myaccount.google.com/)
2. Security → 2-Step Verification (must be enabled)
3. App passwords → Select app → Select device
4. Copy the generated password
5. Use this password in config

More info: https://support.google.com/accounts/answer/185833

---

## MCP Tools

### send_email

Send an email via SMTP/Gmail.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject line
- `body` (string, required): Email body content
- `html` (boolean, optional): Whether body is HTML (default: false)

**Example:**
```json
{
  "to": "recipient@example.com",
  "subject": "Hello from MCP",
  "body": "This is a test email sent via MCP.",
  "html": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent to recipient@example.com",
  "messageId": "<abc123@gmail.com>",
  "subject": "Hello from MCP",
  "timestamp": "2026-03-23T15:00:00.000Z"
}
```

### check_email_config

Check if email server is configured properly.

**Parameters:** None

**Response:**
```json
{
  "configured": true,
  "email": "your@gmail.com",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587
}
```

---

## Integration with Orchestrator

The orchestrator watches the `Approved/` folder and sends emails when files are added.

### Workflow

1. File created with email metadata
2. File moved to `Approved/` folder
3. Orchestrator detects file
4. Extracts email details from frontmatter
5. Calls MCP email server
6. Sends email
7. Moves file to `Done/`

### File Format

```markdown
---
metadata:
  to_email: "recipient@example.com"
  email_subject: "Task Approved"
---

# Approval Details

Your task has been approved and is ready for implementation.

## Next Steps
- Review the approved plan
- Begin implementation
- Update status when complete
```

### Orchestrator Configuration

```bash
# Enable MCP email
set ENABLE_MCP_EMAIL=true

# Set default recipient (optional)
set DEFAULT_EMAIL=admin@example.com

# Run orchestrator
python orchestrator.py
```

---

## Usage Examples

### Standalone Server

```bash
# Run Node.js server
node email_mcp.js

# Run Python server
python mcp_email_server.py

# With credentials
node email_mcp.js --email user@gmail.com --password abc123
```

### Client Library (Python)

```python
from mcp_email_client import MCPEmailClient
import asyncio

async def main():
    client = MCPEmailClient()
    
    # Send email
    result = await client.send_email(
        to="recipient@example.com",
        subject="Test Email",
        body="Hello from MCP!",
        html=False
    )
    
    print(result)

asyncio.run(main())
```

### Synchronous

```python
from mcp_email_client import send_email_sync

result = send_email_sync(
    to="recipient@example.com",
    subject="Test",
    body="Hello!"
)

print(result)
```

---

## Testing

### Test Configuration

```bash
# Node.js
node email_mcp.js --email test@gmail.com --password test123 --save-config

# Python
python mcp_email_server.py --email test@gmail.com --password test123 --save-config
```

### Test Email

```bash
# Using client
python mcp_email_client.py recipient@example.com "Test Subject" "Test Body"
```

---

## Logs

Logs are saved to: `logs/mcp_email_server.log`

Example:
```
2026-03-23 15:00:00 - mcp_email_server - INFO - Starting MCP Email Server...
2026-03-23 15:00:01 - mcp_email_server - INFO - Email configured: user@gmail.com
2026-03-23 15:00:05 - mcp_email_server - INFO - Sending email to: recipient@example.com
2026-03-23 15:00:06 - mcp_email_server - INFO - Email sent successfully: <abc123@gmail.com>
```

---

## Troubleshooting

### "Email not configured"

```bash
# Set credentials
node email_mcp.js --email your@gmail.com --password abc123 --save-config

# Or use environment variables
set EMAIL_ADDRESS=your@gmail.com
set EMAIL_PASSWORD=abc123
```

### "Authentication failed"

- Use App Password, not regular password
- Enable 2-Step Verification in Google Account
- Check password has no spaces

### "MCP client not installed"

```bash
pip install mcp
```

### "Cannot find module '@modelcontextprotocol/sdk'"

```bash
npm install @modelcontextprotocol/sdk
```

---

## Security Notes

1. **Never commit passwords** - Use environment variables or config files
2. **Use App Passwords** - Never use your main Gmail password
3. **Enable 2FA** - Required for app passwords
4. **Restrict access** - Config file should be readable only by owner

---

## API Reference

### Node.js Server

```javascript
const server = new MCPEmailServer();
await server.run();
```

### Python Server

```python
from mcp_email_server import MCPEmailServer, EmailConfig
import asyncio

config = EmailConfig()
server = MCPEmailServer(config)
asyncio.run(server.run())
```

### Client

```python
from mcp_email_client import MCPEmailClient

client = MCPEmailClient()
result = await client.send_email(to, subject, body, html)
config = await client.check_config()
```

---

## Complete Example

### 1. Setup Config

```bash
mkdir -p ~/.config/qwen-code
cat > ~/.config/qwen-code/email_config.json << EOF
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "email": "your@gmail.com",
  "app_password": "your-app-password"
}
EOF
```

### 2. Start MCP Server

```bash
node email_mcp.js
```

### 3. Create Approval File

```markdown
---
metadata:
  to_email: "manager@company.com"
  email_subject: "Project Approved"
---

# Project Approval

The project has been reviewed and approved.

## Budget
$10,000

## Timeline
2 weeks

Please proceed with implementation.
```

### 4. Move to Approved

```bash
mv approval.md AI_Employee_Vault/Silver_Tier/Approved/
```

### 5. Orchestrator Sends Email

```
[INFO] Found 1 approved files to process
[INFO] Sending approval email to: manager@company.com
[INFO] Email sent successfully
[INFO] Moved: approval.md -> Done/
```

---

## Summary

| Feature | Status |
|---------|--------|
| SMTP Support | ✅ |
| Gmail API | ✅ (via SMTP) |
| HTML Emails | ✅ |
| MCP Protocol | ✅ |
| Orchestrator Integration | ✅ |
| Config File | ✅ |
| Environment Variables | ✅ |
| Logging | ✅ |

**Fully functional MCP email server ready!** ✅
