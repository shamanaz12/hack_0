#!/bin/bash

echo "============================================"
echo "  AI Employee Vault - WSL Setup Script"
echo "============================================"
echo ""

# Update system packages
echo "Step 1: Updating system packages..."
sudo apt update -y
echo ""

# Install Python3 and pip
echo "Step 2: Installing Python3 and pip..."
sudo apt install -y python3 python3-pip
echo ""

# Install Python dependencies
echo "Step 3: Installing Python dependencies..."
cd /mnt/c/Users/AA/Desktop/h.p_hack_0/AI_Employee_Vault

pip3 install -r requirements.txt
pip3 install -r requirements_gmail.txt
pip3 install -r requirements_mcp.txt
echo ""

# Check credentials.json
echo "Step 4: Checking credentials.json..."
if [ ! -f "credentials.json" ]; then
    echo ""
    echo "⚠️  credentials.json not found!"
    echo ""
    echo "You need to get this file from Google Cloud Console:"
    echo "1. Go to: https://console.cloud.google.com/"
    echo "2. Create a NEW PROJECT (name: AI-Employee-Vault)"
    echo "3. Enable Gmail API"
    echo "4. Create OAuth 2.0 Client IDs (Desktop app)"
    echo "5. Download JSON and rename to: credentials.json"
    echo "6. Place it in: /mnt/c/Users/AA/Desktop/h.p_hack_0/AI_Employee_Vault/"
    echo ""
else
    echo "✅ credentials.json found!"
fi
echo ""

echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "Next Steps:"
echo "1. Get Gmail App Password from:"
echo "   https://myaccount.google.com/security"
echo ""
echo "2. Run Gmail Watcher (receive emails):"
echo "   python3 gmail_poller.py"
echo ""
echo "3. Run MCP Server (send emails):"
echo "   export SMTP_HOST=smtp.gmail.com"
echo "   export SMTP_PORT=587"
echo "   export SMTP_USERNAME=your-email@gmail.com"
echo "   export SMTP_PASSWORD='your-app-password'"
echo "   python3 mcp_email_server.py"
echo ""
