# WSL Installation Guide for Beginners

## Option 1: Use Windows (Recommended for Beginners) ✅

**You don't need WSL!** Everything works on Windows directly.

### Just run these files:

1. **Double-click:** `INSTALL_AND_RUN.bat` (in AI_Employee_Vault folder)
2. This will install everything on Windows
3. Follow the prompts

---

## Option 2: Install WSL First

### Step 1: Enable WSL (Run in PowerShell as Administrator)

```powershell
wsl --install
```

This will:
- Enable WSL feature
- Install Ubuntu by default
- Require a restart

### Step 2: After Restart

1. Ubuntu will open automatically
2. Create a username and password (remember this!)
3. You're now in Linux terminal

### Step 3: Install Python in WSL

```bash
sudo apt update
sudo apt install -y python3 python3-pip
```

### Step 4: Install Dependencies

```bash
cd /mnt/c/Users/AA/Desktop/h.p_hack_0/AI_Employee_Vault
pip3 install -r requirements.txt
pip3 install -r requirements_gmail.txt
pip3 install -r requirements_mcp.txt
```

### Step 5: Run the System

```bash
# Gmail Watcher (receive emails)
python3 gmail_poller.py

# MCP Server (send emails) - in another terminal
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=your-email@gmail.com
export SMTP_PASSWORD="your-app-password"
python3 mcp_email_server.py
```

---

## ⚡ Quick Comparison

| Feature | Windows | WSL |
|---------|---------|-----|
| Setup | Double-click `.bat` file | Multiple terminal commands |
| Python | Already installed | Need to install |
| Dependencies | Already installed | Need to install |
| Recommended for | **Beginners** ✅ | Advanced users |

---

## 🎯 My Recommendation

**Use Windows!** Just double-click:
```
INSTALL_AND_RUN.bat
```

Everything is already set up for Windows. No need for WSL unless you specifically need Linux.

---

## 📋 After Setup (Both Windows/WSL)

You still need to:

1. **Get credentials.json** from Google Cloud Console
   - Go to: https://console.cloud.google.com/
   - Create project → Enable Gmail API → Create OAuth credentials

2. **Get Gmail App Password**
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification → Generate App Password

3. **Run the system**
   - Windows: Double-click `start_gmail_watcher.bat`
   - WSL: Run `python3 gmail_poller.py`

---

## ❓ Need Help?

Read: `QUICK_START_GUIDE.md` for detailed step-by-step instructions.
