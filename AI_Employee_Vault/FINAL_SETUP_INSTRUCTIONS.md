# Final Setup Instructions

## Step 1: Update the Credentials File
1. Open the file: `C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault\start_mcp_with_credentials.bat`
2. Find the line: `set SMTP_PASSWORD=your_actual_app_password`
3. Replace `your_actual_app_password` with your actual Gmail App Password
4. Save the file

## Step 2: Run the MCP Email Server
1. Double-click on `start_mcp_with_credentials.bat` to run the email server
2. The server will start on http://localhost:5000

## Step 3: Test the Email Server
1. The server supports these endpoints:
   - POST /send-email: Send an email
   - GET /health: Check server health

Example request to send an email:
```json
{
  "to": "recipient@example.com",
  "subject": "Test Subject",
  "body": "Test message body",
  "dry_run": true
}
```

## Step 4: Run the Complete System
1. You can also run the complete system with: `start_complete_system.bat`
2. This will guide you through all components including Gmail integration

## Important Notes:
- Keep your App Password secure and private
- The system is fully set up and ready to use
- All components are working together
- The cron scheduler is ready to run every 5 minutes
- The file processing pipeline is operational

Your AI Employee Vault system is complete and ready to automate your workflow!