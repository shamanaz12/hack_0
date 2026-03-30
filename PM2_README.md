# PM2 Setup Guide - Gold Tier
## Complete Process Management

---

## 📋 **PREREQUISITES**

### Install Node.js
Download from: https://nodejs.org/

### Install PM2 Globally
```bash
npm install -g pm2
```

### Verify Installation
```bash
pm2 --version
```

---

## 🚀 **QUICK START**

### Start All Services
```bash
cd C:\Users\AA\Desktop\gold_tier
pm2 start ecosystem.config.js
```

### Start Specific Service
```bash
# Facebook Watcher only
pm2 start ecosystem.config.js --only facebook-watcher

# Gmail Watcher only
pm2 start ecosystem.config.js --only gmail-watcher

# All MCP servers
pm2 start ecosystem.config.js --only mcp-email-server
```

---

## 📊 **MONITORING**

### View All Processes
```bash
pm2 list
```

### Real-time Monitoring
```bash
pm2 monit
```

### View Logs
```bash
# All logs
pm2 logs

# Specific service logs
pm2 logs facebook-watcher

# Clear logs
pm2 flush
```

---

## 🔄 **MANAGEMENT**

### Restart Services
```bash
# Restart all
pm2 restart ecosystem.config.js

# Restart specific
pm2 restart facebook-watcher

# Restart with force (kill + restart)
pm2 restart facebook-watcher --force
```

### Stop Services
```bash
# Stop all
pm2 stop ecosystem.config.js

# Stop specific
pm2 stop facebook-watcher
```

### Delete Services
```bash
# Delete all
pm2 delete ecosystem.config.js

# Delete specific
pm2 delete facebook-watcher
```

---

## ⚙️ **ADVANCED COMMANDS**

### Force Re-execution (Kill + Restart)
```bash
pm2 restart facebook-watcher --force
```

### Reload Configuration
```bash
pm2 reload ecosystem.config.js
```

### Update Environment Variables
```bash
pm2 restart facebook-watcher --update-env
```

### Save Process List (Auto-start on boot)
```bash
pm2 save
pm2 startup
```

### Scale Instances (for Node.js apps)
```bash
pm2 start app.js -i 4  # 4 instances
pm2 scale facebook-watcher 2  # 2 instances
```

---

## 📝 **SERVICES CONFIGURED**

| Service Name | Script | Port | Description |
|--------------|--------|------|-------------|
| `facebook-watcher` | watcher/facebook_instagram_watcher.py | - | Monitors FB/IG |
| `gmail-watcher` | gmail_watcher.py | - | Gmail monitoring |
| `whatsapp-watcher` | whatsapp_watcher.py | - | WhatsApp monitoring |
| `orchestrator` | orchestrator.py | - | File orchestrator |
| `scheduler` | scheduler.py | - | Cron scheduler |
| `auto-processor` | auto_processor.py | - | Auto processor |
| `mcp-email-server` | mcp_email_server.py | - | Email MCP |
| `odoo-mcp-server` | odoo_mcp_server.py | - | Odoo MCP |

---

## 🔧 **PM2 BATCH FILES**

### Start All Services
```bash
pm2_start_all.bat
```

### Stop All Services
```bash
pm2_stop_all.bat
```

### Restart All Services
```bash
pm2_restart_all.bat
```

### View Status
```bash
pm2_status.bat
```

### View Logs
```bash
pm2_logs.bat
```

---

## 🎯 **FACEBOOK WATCHER SPECIFIC**

### Start Facebook Watcher
```bash
pm2 start ecosystem.config.js --only facebook-watcher
```

### Check Status
```bash
pm2 status facebook-watcher
```

### View Logs
```bash
pm2 logs facebook-watcher
```

### Force Restart
```bash
pm2 restart facebook-watcher --force
```

### Stop
```bash
pm2 stop facebook-watcher
```

### Delete
```bash
pm2 delete facebook-watcher
```

---

## 📊 **LOGS LOCATION**

All PM2 logs saved in:
```
C:\Users\AA\Desktop\gold_tier\logs\pm2-*.log
```

Files:
- `pm2-facebook-watcher-error.log` - Error logs
- `pm2-facebook-watcher-out.log` - Output logs
- `pm2-facebook-watcher-combined.log` - Combined logs

---

## ⚠️ **TROUBLESHOOTING**

### Service Won't Start
```bash
# Check logs
pm2 logs facebook-watcher --err

# Check if script exists
dir watcher\facebook_instagram_watcher.py

# Check Python path
where python
```

### High Memory Usage
```bash
# Restart with memory limit
pm2 restart facebook-watcher --max-memory-restart 500M
```

### Service Crashes Repeatedly
```bash
# Check error logs
pm2 logs facebook-watcher --lines 100

# Disable auto-restart temporarily
pm2 restart facebook-watcher --no-autorestart
```

### Port Already in Use
```bash
# Find process using port
netstat -ano | findstr :3000

# Kill process
taskkill /F /PID <PID>

# Restart service
pm2 restart service-name
```

---

## 🎉 **COMPLETE SETUP**

1. Install PM2: `npm install -g pm2`
2. Go to folder: `cd C:\Users\AA\Desktop\gold_tier`
3. Start all: `pm2 start ecosystem.config.js`
4. Check status: `pm2 list`
5. View logs: `pm2 logs`

---

**All set! PM2 managing all Gold Tier services!** 🚀
