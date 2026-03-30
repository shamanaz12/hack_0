# Gmail Watcher for AI Employee Vault

This system monitors your Gmail inbox, extracts information from unread emails, and creates markdown files in the Needs_Action folder for processing.

## Prerequisites

- Python 3.6 or higher
- Google Account with Gmail enabled
- Google Cloud Platform account

## Setup Instructions

### 1. Google API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and click on it
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Select "Desktop application" as the application type
   - Give it a name (e.g., "Gmail Watcher")
   - Click "Create"
5. Download the credentials JSON file
6. Rename the downloaded file to `credentials.json`
7. Place the `credentials.json` file in the AI_Employee_Vault directory

### 2. Install Dependencies

```bash
pip install -r requirements_gmail.txt
```

### 3. Run the Gmail Watcher

```bash
python gmail_poller.py
```

On the first run, you'll be prompted to authenticate with your Google account. Follow the instructions in the console to complete the OAuth flow.

## How It Works

1. The system checks your Gmail inbox every 5 minutes
2. It looks specifically for unread emails in your inbox
3. For each unread email, it extracts:
   - Sender (from)
   - Subject
   - Email snippet (preview text)
   - Timestamp
4. Creates a markdown file in the `Needs_Action` folder with the extracted information
5. The markdown file includes action items to process the email

## Security

- Uses OAuth2 for secure authentication
- Tokens are stored locally in `token.pickle`
- No passwords are stored in the application
- Only read-only access to Gmail is requested

## Files Created

- `gmail_watcher.log` - Logs all activity and errors
- `token.pickle` - Stores authentication tokens (securely)
- `credentials.json` - Your Google API credentials (keep this secure!)
- Markdown files in `Needs_Action` folder for each unread email

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you've installed all dependencies
2. **Authentication errors**: Delete `token.pickle` and restart the application to re-authenticate
3. **API quota exceeded**: The system respects Gmail API quotas, but heavy usage might hit limits

### Logs

Check `gmail_watcher.log` for detailed information about what the system is doing and any errors that occur.

## Stopping the Service

Press `Ctrl+C` to stop the Gmail watcher service.

## Configuration

The polling interval is set to 5 minutes (300 seconds) by default. To change this, modify the `poll_interval` variable in `gmail_poller.py`.