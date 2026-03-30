# AI Employee Vault - Two Tier System

## Overview

This project now has **2 separate tiers** for different levels of automation:

| Tier | Purpose | Gmail Integration | MCP Connection | User Limit |
|------|---------|-------------------|----------------|------------|
| **Bronze Tier** | Testing Mode | Basic (OAuth Testing) | ❌ No | 100 users |
| **Silver Tier** | Production Mode | Full (Verified OAuth) | ✅ Yes | Unlimited |

---

## 🥉 Bronze Tier (Testing Mode)

### Folder Structure:
```
Bronze_Tier/
├── inbox/           # Incoming emails are stored here
├── skills/          # Categorized tasks by skill/type
├── Needs_Action/    # Emails requiring response/action
└── Done/            # Completed responses (auto-moved from Needs_Action)
```

### Workflow:
```
Gmail → inbox → Needs_Action → [Your Response] → Done
              ↓
          skills (categorized)
```

### Features:
- ✅ Basic Gmail API access (testing mode)
- ✅ Email to markdown conversion
- ✅ Manual response workflow
- ❌ No MCP server integration
- ❌ No automated email sending

### Use Case:
- Testing and development
- Personal automation (< 100 users)
- Manual review before sending

---

## 🥈 Silver Tier (Production Mode)

### Folder Structure:
```
Silver_Tier/
├── inbox/              # Incoming emails from Gmail API
├── skills/             # AI-categorized tasks by skill
├── Needs_Action/       # Emails requiring action
├── Done/               # Auto-completed after MCP sends response
├── LinkedIn_Drafts/    # 🎯 LinkedIn post drafts (auto-generated)
└── Logs/               # MCP and automation logs
```

### Workflow:
```
Gmail → inbox → Needs_Action → [MCP Auto-Response] → Done
              ↓
          skills (AI categorized)
```

### Features:
- ✅ Full Gmail API access (verified)
- ✅ MCP Email Server integration
- ✅ Automated email responses
- ✅ AI-powered skill categorization
- ✅ **LinkedIn post generator** (auto-create posts from campaigns)
- ✅ Unlimited users

### Use Case:
- Production deployment
- Automated email responses
- High-volume email processing

---

## 📁 Folder Descriptions

### `inbox/`
- **Purpose**: Raw incoming emails from Gmail
- **Auto-created by**: `gmail_poller.py`
- **Format**: Markdown files with email metadata

### `skills/`
- **Purpose**: Categorized tasks by type/skill
- **Categories**:
  - `email_campaigns/` - Marketing emails
  - `customer_support/` - Support requests
  - `meetings/` - Meeting requests
  - `general/` - Other tasks
- **Auto-categorized by**: AI analysis

### `Needs_Action/`
- **Purpose**: Emails requiring your response/action
- **Workflow**: Review → Approve → Send Response
- **Status**: Pending

### `Done/`
- **Purpose**: Completed tasks
- **Auto-moved from**: `Needs_Action/` after response sent
- **Format**: `COMPLETED_<original_filename>.md`

---

## 🔄 Email Flow (Bronze vs Silver)

### Bronze Tier Flow:
```
1. Email arrives in Gmail
2. gmail_poller.py copies to Bronze_Tier/inbox/
3. File moved to Bronze_Tier/Needs_Action/
4. You review and create response manually
5. File moved to Bronze_Tier/Done/
```

### Silver Tier Flow:
```
1. Email arrives in Gmail
2. gmail_poller.py copies to Silver_Tier/inbox/
3. AI categorizes into Silver_Tier/skills/[category]/
4. File moved to Silver_Tier/Needs_Action/
5. MCP Server auto-sends response
6. File auto-moved to Silver_Tier/Done/
7. LinkedIn post auto-generated in Silver_Tier/LinkedIn_Drafts/
```

---

## 🚀 Quick Start

### Bronze Tier (Start Here for Testing):
```bash
cd C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault

# 1. Setup OAuth (follow prompts)
python gmail_auth.py

# 2. Start Gmail watcher
python gmail_poller.py

# 3. Check Bronze_Tier/Needs_Action/ for new emails
```

### Silver Tier (Production):
```bash
cd C:\Users\AA\Desktop\h.p_hack_0\AI_Employee_Vault

# 1. Setup MCP Server credentials
# Edit start_mcp_with_credentials.bat with your Gmail App Password

# 2. Start MCP Server
start_mcp_with_credentials.bat

# 3. Start Gmail watcher for Silver Tier
python gmail_poller.py --tier silver

# 4. Monitor Silver_Tier/Done/ for completed responses
```

---

## 📊 Current Status

| Component | Bronze Tier | Silver Tier |
|-----------|-------------|-------------|
| Folders Created | ✅ | ✅ |
| inbox/ | ✅ | ✅ |
| skills/ | ✅ | ✅ |
| Needs_Action/ | ✅ | ✅ |
| Done/ | ✅ | ✅ |
| Gmail Integration | ⚠️ Setup Needed | ⚠️ Setup Needed |
| MCP Integration | ❌ Not Available | ⚠️ Setup Needed |

---

## 🎯 Next Steps

1. **For Bronze Tier:**
   - Complete OAuth setup (see `QUICK_START_GUIDE.md`)
   - Run `gmail_poller.py`
   - Test manual workflow

2. **For Silver Tier:**
   - Complete OAuth verification (Google Cloud Console)
   - Setup MCP Server with App Password
   - Enable automated responses

---

## 📝 File Naming Convention

- **inbox/**: `Gmail_YYYYMMDD_HHMMSS_Subject.md`
- **skills/**: `[category]_YYYYMMDD_HHMMSS_Subject.md`
- **Needs_Action/**: `NA_YYYYMMDD_HHMMSS_Subject.md`
- **Done/**: `COMPLETED_YYYYMMDD_HHMMSS_Subject.md`
