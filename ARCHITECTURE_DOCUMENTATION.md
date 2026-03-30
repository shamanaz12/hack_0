# 🏗️ GOLD TIER - SYSTEM ARCHITECTURE DOCUMENTATION

**Autonomous Employee System**  
**Version:** 1.0  
**Last Updated:** March 28, 2026  
**Status:** ✅ PRODUCTION READY

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Tier Structure](#tier-structure)
6. [Integration Points](#integration-points)

---

## 🎯 SYSTEM OVERVIEW

The Gold Tier system is an **autonomous employee automation platform** that integrates multiple communication and business platforms without requiring API tokens. It uses browser automation (Playwright) combined with MCP (Model Context Protocol) servers to provide seamless automation for:

- **Email** (Gmail)
- **Messaging** (WhatsApp)
- **Social Media** (Facebook, Instagram)
- **Business Operations** (Odoo ERP)

### Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **Token-Free** | No API tokens required - uses browser sessions |
| 🤖 **AI-Powered** | Qwen AI integration for content generation |
| 📊 **Audit Ready** | Complete audit logging for all actions |
| 🔄 **Auto-Recovery** | Circuit breakers and retry logic |
| 📁 **Tier-Based** | Bronze → Silver → Gold progression |

---

## 🏛️ ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI LAYER (Qwen AI)                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  • Content Generation    • Decision Making                      │   │
│  │  • Natural Language      • Report Generation                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION LAYER                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │   Master         │  │   Ralph Loop     │  │   Error          │     │
│  │   Orchestrator   │  │   (Autonomous)   │  │   Recovery       │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    Audit Logger                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       MCP SERVER LAYER                                  │
│                                                                         │
│  ┌─────────────────────────┐  ┌─────────────────────────┐              │
│  │   COMMUNICATION MCP     │  │    SOCIAL MEDIA MCP     │              │
│  │  ┌──────────────────┐  │  │  ┌──────────────────┐  │              │
│  │  │  Gmail MCP       │  │  │  │  Facebook MCP    │  │              │
│  │  │  (SMTP/IMAP)     │  │  │  │  (Playwright)    │  │              │
│  │  └──────────────────┘  │  │  └──────────────────┘  │              │
│  │  ┌──────────────────┐  │  │  ┌──────────────────┐  │              │
│  │  │  WhatsApp MCP    │  │  │  │  Instagram MCP   │  │              │
│  │  │  (Browser)       │  │  │  │  (Browser)       │  │              │
│  │  └──────────────────┘  │  │  └──────────────────┘  │              │
│  └─────────────────────────┘  └─────────────────────────┘              │
│                                                                         │
│  ┌─────────────────────────┐                                           │
│  │    BUSINESS MCP         │                                           │
│  │  ┌──────────────────┐  │                                           │
│  │  │  Odoo MCP        │  │                                           │
│  │  │  (JSON-RPC)      │  │                                           │
│  │  └──────────────────┘  │                                           │
│  └─────────────────────────┘                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        TOOLS LAYER                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │  SMTP/IMAP   │  │  Playwright  │  │  JSON-RPC    │  │  REST API  │ │
│  │  (Email)     │  │  (Browser)   │  │  (Odoo)      │  │  (OAuth)   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      WORKFLOW LAYER                                     │
│                                                                         │
│   ┌────────────┐    ┌────────────┐    ┌────────────┐                  │
│   │  Bronze    │ →  │   Silver   │ →  │    Gold    │                  │
│   │  (Basic)   │    │ (Advanced) │    │ (Complete) │                  │
│   └────────────┘    └────────────┘    └────────────┘                  │
│                                                                         │
│   Workflow: needs_action → logs → plans → inbox/approve → done         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 COMPONENT DETAILS

### 1. AI Layer (Qwen AI)

**Purpose:** Provides intelligent decision-making and content generation

| Component | File | Function |
|-----------|------|----------|
| Content Generator | `ai_auto_post.py` | Generates social media posts |
| Decision Engine | `ralph_loop.py` | Autonomous task execution |
| Report Generator | `weekly_audit.py` | Creates audit reports |

**Configuration:**
```env
DASHSCOPE_API_KEY=your_key
MODEL_NAME=qwen-plus
MAX_ITERATIONS=10
```

---

### 2. Orchestration Layer

**Purpose:** Coordinates all system components and manages workflows

#### Master Orchestrator
**File:** `master_orchestrator.py`

```
┌─────────────────────────────────────────┐
│         MASTER ORCHESTRATOR             │
├─────────────────────────────────────────┤
│  • Service Discovery                    │
│  • Health Monitoring                    │
│  • Start/Stop Control                   │
│  • State Management                     │
└─────────────────────────────────────────┘
```

**Commands:**
```bash
python master_orchestrator.py start    # Start all services
python master_orchestrator.py stop     # Stop all services
python master_orchestrator.py status   # Check status
python master_orchestrator.py health   # Health check
```

#### Ralph Loop (Autonomous Agent)
**File:** `ralph_loop.py`

```
┌─────────────────────────────────────────┐
│           RALPH LOOP                    │
│                                         │
│   Plan → Execute → Verify → Repair     │
│           ↓                             │
│        Continue                         │
└─────────────────────────────────────────┘
```

**Workflow:**
1. **Plan:** Analyze needs_action folder
2. **Execute:** Perform required actions
3. **Verify:** Check results
4. **Repair:** Handle errors
5. **Continue:** Move to next task

---

### 3. MCP Server Layer

#### Communication MCP
**Folder:** `mcp_servers/communication/`

| Server | Protocol | Port | Status |
|--------|----------|------|--------|
| Gmail MCP | SMTP/IMAP | - | ✅ Active |
| WhatsApp MCP | Browser | - | ✅ Active |

**Gmail Configuration:**
```env
GMAIL_SMTP_HOST=smtp.gmail.com
GMAIL_SMTP_PORT=587
GMAIL_EMAIL=naz.sheikh.business@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

---

#### Social Media MCP
**Folder:** `mcp_servers/social_media/`

| Server | Technology | Port | Status |
|--------|------------|------|--------|
| Facebook MCP | Playwright | 8080 | ✅ Active |
| Instagram MCP | Browser | 3001 | ✅ Active |

**Facebook Configuration:**
```env
FACEBOOK_PAGE_ID=61578524116357
FACEBOOK_EMAIL=naz sheikh
FACEBOOK_PASSWORD=uzain786
FACEBOOK_PORT=8080
```

**Instagram Configuration:**
```env
INSTAGRAM_USERNAME=shamaansari5576
INSTAGRAM_PASSWORD=your_password
INSTAGRAM_PORT=3001
```

---

#### Business MCP
**Folder:** `mcp_servers/business/`

| Server | Protocol | Port | Status |
|--------|----------|------|--------|
| Odoo MCP | JSON-RPC | 8069 | ✅ Active |

**Odoo Configuration:**
```env
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=admin
```

---

### 4. Tools Layer

| Tool | Purpose | Implementation |
|------|---------|----------------|
| SMTP/IMAP | Email sending/receiving | Python `smtplib`, `imaplib` |
| Playwright | Browser automation | Python `playwright` |
| JSON-RPC | Odoo communication | Python `requests` |
| REST API | External integrations | Python `requests` |

---

### 5. Workflow Layer (Tier System)

```
┌──────────────────────────────────────────────────────────────────┐
│                        TIER PROGRESSION                          │
│                                                                  │
│   ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │
│   │   BRONZE    │  →   │   SILVER    │  →   │    GOLD     │    │
│   │             │      │             │      │             │    │
│   │ Basic       │      │ Advanced    │      │ Complete    │    │
│   │ Automation  │      │ Integration │      │ System      │    │
│   └─────────────┘      └─────────────┘      └─────────────┘    │
│                                                                  │
│   Files: 1-5            Files: 5-15          Files: 15+         │
│   Platforms: 1          Platforms: 2-3       Platforms: 4+      │
│   Manual: High          Manual: Medium       Manual: Low        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 DATA FLOW

### Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW DIAGRAM                               │
└─────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   User      │
    │   Input     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐
    │  AI_Employee    │
    │  Vault          │
    │  (Storage)      │
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    WORKFLOW PROCESSING                          │
    │                                                                 │
    │   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
    │   │  Needs   │ →  │   Logs   │ →  │  Plans   │ →  │  Inbox   │ │
    │   │  Action  │    │          │    │          │    │          │ │
    │   └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
    │                                              │                  │
    │                                              ▼                  │
    │                                       ┌──────────┐             │
    │                                       │   Done   │             │
    │                                       └──────────┘             │
    └─────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    MCP SERVER EXECUTION                         │
    │                                                                 │
    │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
    │   │  Email MCP   │  │  Social MCP  │  │  Business MCP│        │
    │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘        │
    └──────────┼─────────────────┼─────────────────┼─────────────────┘
               │                 │                 │
               ▼                 ▼                 ▼
        ┌────────────┐   ┌────────────┐   ┌────────────┐
        │   Gmail    │   │  Facebook  │   │    Odoo    │
        │  WhatsApp  │   │ Instagram  │   │  Invoicing │
        └────────────┘   └────────────┘   └────────────┘
```

### Post Creation Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                      POST CREATION FLOW                              │
└──────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐
    │   Topic     │
    │   Input     │
    └──────┬──────┘
           │
           ▼
    ┌─────────────────┐
    │  AI Generates   │
    │  Content        │
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │  Save to        │
    │  posts/         │
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │  Queue for      │
    │  Publishing     │
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │  Publish via    │
    │  MCP Server     │
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │  Log to         │
    │  logs/          │
    └──────┬──────────┘
           │
           ▼
    ┌─────────────────┐
    │  Move to        │
    │  Done/          │
    └─────────────────┘
```

---

## 📊 TIER STRUCTURE

### Bronze Tier

**Status:** ✅ COMPLETE

| Feature | Description |
|---------|-------------|
| Platforms | Single platform (Email) |
| Automation | Basic file watchers |
| AI Integration | Minimal |
| Files | 1-5 scripts |

**Components:**
- Gmail watcher
- Basic email sending
- Simple logging

---

### Silver Tier

**Status:** ✅ COMPLETE

| Feature | Description |
|---------|-------------|
| Platforms | 2-3 platforms |
| Automation | Intermediate workflows |
| AI Integration | Content generation |
| Files | 5-15 scripts |

**Components:**
- Email + WhatsApp
- Social media posting
- Basic orchestration

---

### Gold Tier

**Status:** ✅ COMPLETE

| Feature | Description |
|---------|-------------|
| Platforms | 4+ platforms |
| Automation | Full autonomous agent |
| AI Integration | Complete AI integration |
| Files | 15+ scripts |

**Components:**
- Gmail + WhatsApp + Facebook + Instagram + Odoo
- Ralph Loop autonomous agent
- Weekly audit reports
- CEO briefings
- Error recovery system
- Complete audit logging

---

## 🔗 INTEGRATION POINTS

### External Systems

| System | Integration Method | Status |
|--------|-------------------|--------|
| Gmail | SMTP/IMAP | ✅ Active |
| WhatsApp | Browser Automation | ✅ Active |
| Facebook | Playwright | ✅ Active |
| Instagram | Browser Automation | ✅ Active |
| Odoo | JSON-RPC | ✅ Active |
| Qwen AI | Dashscope API | ✅ Active |

### Internal Systems

| System | Purpose | Location |
|--------|---------|----------|
| AI_Employee_Vault | File storage | `AI_Employee_Vault/` |
| Logs | Audit trail | `logs/` |
| Reports | Generated reports | `reports/` |
| PIDs | Process tracking | `pids/` |

---

## 📁 FOLDER STRUCTURE

```
gold_tier/
├── mcp_servers/                    # MCP Servers
│   ├── communication/              # Email + WhatsApp
│   ├── social_media/               # Facebook + Instagram
│   ├── business/                   # Odoo + Accounting
│   ├── gmail_mcp_server.py
│   ├── whatsapp_mcp.js
│   ├── facebook_mcp_playwright.py
│   └── instagram_mcp.js
│
├── AI_Employee_Vault/              # Workflow Storage
│   ├── Bronze_Tier/
│   ├── Silver_Tier/
│   └── Gold_Tier/
│       ├── Needs_Action/
│       ├── Logs/
│       ├── Plans/
│       ├── inbox/
│       └── Done/
│
├── automation/                     # Automation Scripts
│   └── weekly_audit_automation.py
│
├── orchestration/                  # Orchestration
│   ├── master_orchestrator.py
│   ├── ralph_loop.py
│   └── error_recovery.py
│
├── logs/                           # System Logs
│ ├── facebook_posts.json
│ ├── instagram_posts.json
│ └── whatsapp_outgoing.json
│
├── reports/                        # Generated Reports
│ ├── weekly_audit_*.md
│ └── ceo_briefing_*.md
│
├── posts/                          # Queued Posts
├── pids/                           # Process IDs
├── plans/                          # Generated Plans
├── backup/                         # Backups
│
├── .env                            # Configuration
├── master_orchestrator.py          # Main Orchestrator
├── ralph_loop.py                   # Autonomous Agent
├── audit_logger.py                 # Audit Logging
└── GOLD_TIER_START.bat             # Quick Start
```

---

## 🚀 QUICK START

### Start All Services
```bash
GOLD_TIER_START.bat
# Select option 5: Start All Services
```

### Health Check
```bash
python master_orchestrator.py health
```

### Generate AI Post
```bash
generate_post.bat
```

### Run Autonomous Agent
```bash
run_autonomous_agent.bat
```

---

## 📞 SUPPORT

For issues or questions:
1. Check logs in `logs/` folder
2. Review `COMPLETE_ARCHITECTURE.md`
3. Run health check: `python master_orchestrator.py health`

---

**Document Version:** 1.0  
**Last Updated:** March 28, 2026  
**Maintained By:** Gold Tier Team
