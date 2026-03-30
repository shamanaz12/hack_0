# 🚀 GOLD TIER - QUICK START GUIDE
# فوری شروعاتی گائیڈ

**Last Updated:** March 26, 2026  
**For:** Naz Sheikh - Gold Tier System

---

## ⚡ SUPER QUICK START (3 Steps)

### Step 1: Double Click This File
```
GOLD_TIER_START.bat
```

### Step 2: Select Option 2 (Install Dependencies)
```
Wait for installation to complete
```

### Step 3: Select Option 3 (Start All Services)
```
All services will start automatically
```

**Done! ✅** System is running.

---

## 📋 COMPLETE SETUP GUIDE

### 1️⃣ Install Dependencies (One Time)

**Option A: Using Batch File**
```
Double click: GOLD_TIER_START.bat
Select: 2 (Install Dependencies)
```

**Option B: Manual Commands**
```bash
# Open Command Prompt in gold_tier folder
cd C:\Users\AA\Desktop\gold_tier

# Install Python packages
pip install requests python-dotenv watchdog dashscope

# Install Node.js packages
npm install express axios dotenv
```

---

### 2️⃣ Configure System

**Option A: Interactive Setup (Recommended)**
```
Double click: GOLD_TIER_START.bat
Select: 1 (Configure System)
Follow the prompts
```

**Option B: Manual .env Edit**
```
1. Open: .env file in Notepad
2. Update these values:

FACEBOOK_PAGE_ACCESS_TOKEN=your_token_here
FACEBOOK_PAGE_ID=956241877582673

INSTAGRAM_BUSINESS_ID=your_instagram_id
INSTAGRAM_ACCESS_TOKEN=your_token_here

ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

3. Save file
```

---

### 3️⃣ Get Facebook Token (Optional for Now)

**Run Helper Script:**
```
Double click: GOLD_TIER_START.bat
Select: 7 (Get Facebook Token)
Follow step-by-step guide
```

**Or Manual:**
1. Visit: https://developers.facebook.com/tools/explorer/
2. Generate token with permissions
3. Copy token to .env file

---

### 4️⃣ Start Services

**Start Everything:**
```
Double click: GOLD_TIER_START.bat
Select: 3 (Start All Services)
```

**Start Individual Services:**
```
# Facebook MCP
Select: 10

# Instagram MCP
Select: 11

# Odoo MCP
Select: 12
```

---

## 🎯 COMMON COMMANDS

### Check Status
```
Double click: GOLD_TIER_START.bat
Select: 5 (Check Status)
```

Or:
```bash
python master_orchestrator.py status
```

### Health Check
```
Double click: GOLD_TIER_START.bat
Select: 6 (Health Check)
```

Or:
```bash
python master_orchestrator.py health
```

### Run Weekly Audit
```
Double click: GOLD_TIER_START.bat
Select: 8 (Run Weekly Audit)
```

Or:
```bash
python master_orchestrator.py audit
```

### Generate Reports
```
Double click: GOLD_TIER_START.bat
Select: 9 (Generate Reports)
```

Or:
```bash
python master_orchestrator.py report
```

---

## 📁 IMPORTANT FILES

| File | Purpose |
|------|---------|
| `GOLD_TIER_START.bat` | Main menu - Start here! |
| `.env` | Configuration file |
| `configure_system.py` | Interactive setup wizard |
| `get_facebook_token.py` | Facebook token helper |
| `master_orchestrator.py` | Main control system |
| `GOLD_TIER_COMPLETE.md` | Full documentation |

---

## 🔧 TROUBLESHOOTING

### Problem: "Python not found"
**Solution:**
```
1. Install Python 3.8+ from python.org
2. During installation, check "Add Python to PATH"
3. Restart computer
4. Try again
```

### Problem: "Node.js not found"
**Solution:**
```
1. Install Node.js from nodejs.org
2. Use LTS version
3. Restart computer
4. Try again
```

### Problem: "Module not found"
**Solution:**
```
Run: GOLD_TIER_START.bat → Option 2
```

### Problem: "Port already in use"
**Solution:**
```
1. Stop all services (Option 4)
2. Wait 10 seconds
3. Start again (Option 3)
```

### Problem: "Cannot connect to Odoo"
**Solution:**
```
1. Make sure Odoo is running
2. Check: http://localhost:8069
3. Verify credentials in .env file
```

---

## 📊 SERVICE PORTS

| Service | Port | URL |
|---------|------|-----|
| Facebook MCP | 3000 | http://localhost:3000 |
| Instagram MCP | 3001 | http://localhost:3001 |
| Odoo | 8069 | http://localhost:8069 |
| Email MCP | N/A | Python script |

---

## ✅ CONFIGURATION CHECKLIST

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Dependencies installed (Option 2)
- [ ] .env file configured
- [ ] Facebook Page ID: 956241877582673 ✓
- [ ] Facebook Token: (optional for now)
- [ ] Odoo running (if using)
- [ ] Services started (Option 3)

---

## 🎓 NEXT STEPS

After basic setup:

1. **Get Facebook Token** (Option 7)
2. **Configure Instagram** (connect to Facebook page)
3. **Setup Gmail App Password**
4. **Configure Odoo** (if using accounting)
5. **Run First Audit** (Option 8)

---

## 📞 SUPPORT FILES

- **Full Documentation:** `GOLD_TIER_COMPLETE.md`
- **Token Guide:** `GET_TOKEN_EASY.md`
- **Facebook Setup:** `facebook_setup_guide.md`
- **Odoo Setup:** `ODOO_MCP_README.md`

---

## 🎉 YOU'RE READY!

**System is configured and running!**

For daily use:
```
Double click: GOLD_TIER_START.bat
Select: 3 (Start All Services)
```

To check status anytime:
```
Select: 5 (Check Status)
```

---

**Created for:** Naz Sheikh  
**Gold Tier - Autonomous Employee System**  
**March 26, 2026**
