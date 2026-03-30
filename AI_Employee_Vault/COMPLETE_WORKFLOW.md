# Gold Tier - Complete Workflow System

## 📋 WORKFLOW FOR EACH SERVICE

```
needs_action → logs → plans → inbox/approve → done
```

---

## 🎯 SERVICES & SKILLS

### 1. **Facebook Watcher**
- **Skill File:** `skills/facebook_watcher_skill.py`
- **Workflow:**
  1. `Needs_Action/facebook_post_request.md` - New post request
  2. `Logs/facebook_YYYYMMDD.log` - Activity logs
  3. `Plans/facebook_post_plan.md` - Post plan
  4. `Inbox/facebook_post_approval.md` - Approval needed
  5. `Done/facebook_post_YYYYMMDD.md` - Completed

### 2. **Instagram Watcher**
- **Skill File:** `skills/instagram_watcher_skill.py`
- **Workflow:**
  1. `Needs_Action/instagram_post_request.md`
  2. `Logs/instagram_YYYYMMDD.log`
  3. `Plans/instagram_post_plan.md`
  4. `Inbox/instagram_post_approval.md`
  5. `Done/instagram_post_YYYYMMDD.md`

### 3. **Gmail Watcher**
- **Skill File:** `skills/gmail_watcher_skill.py`
- **Workflow:**
  1. `Needs_Action/email_request.md`
  2. `Logs/gmail_YYYYMMDD.log`
  3. `Plans/email_plan.md`
  4. `Inbox/email_approval.md`
  5. `Done/email_sent_YYYYMMDD.md`

### 4. **WhatsApp Watcher**
- **Skill File:** `skills/whatsapp_watcher_skill.py`
- **Workflow:**
  1. `Needs_Action/whatsapp_message_request.md`
  2. `Logs/whatsapp_YYYYMMDD.log`
  3. `Plans/whatsapp_plan.md`
  4. `Inbox/whatsapp_approval.md`
  5. `Done/whatsapp_sent_YYYYMMDD.md`

### 5. **Calendar MCP**
- **Skill File:** `skills/calendar_skill.py`
- **Workflow:**
  1. `Needs_Action/event_request.md`
  2. `Logs/calendar_YYYYMMDD.log`
  3. `Plans/event_plan.md`
  4. `Inbox/event_approval.md`
  5. `Done/event_created_YYYYMMDD.md`

### 6. **Slack MCP**
- **Skill File:** `skills/slack_skill.py`
- **Workflow:**
  1. `Needs_Action/slack_message_request.md`
  2. `Logs/slack_YYYYMMDD.log`
  3. `Plans/slack_plan.md`
  4. `Inbox/slack_approval.md`
  5. `Done/slack_sent_YYYYMMDD.md`

### 7. **Odoo MCP**
- **Skill File:** `skills/odoo_skill.py`
- **Workflow:**
  1. `Needs_Action/invoice_request.md`
  2. `Logs/odoo_YYYYMMDD.log`
  3. `Plans/invoice_plan.md`
  4. `Inbox/invoice_approval.md`
  5. `Done/invoice_created_YYYYMMDD.md`

---

## 📁 FOLDER STRUCTURE

```
AI_Employee_Vault/
├── Bronze_Tier/
│   ├── Needs_Action/          # New requests come here
│   ├── Logs/                  # Activity logs
│   ├── Plans/                 # Processing plans
│   ├── inbox/                 # Awaiting approval
│   ├── Done/                  # Completed tasks
│   └── skills/                # Skill files
│       ├── facebook_watcher_skill.py
│       ├── instagram_watcher_skill.py
│       ├── gmail_watcher_skill.py
│       ├── whatsapp_watcher_skill.py
│       ├── calendar_skill.py
│       ├── slack_skill.py
│       └── odoo_skill.py
│
├── Silver_Tier/
│   ├── Needs_Action/
│   ├── Logs/
│   ├── Plans/
│   ├── inbox/
│   ├── Done/
│   └── skills/
│
└── Gold_Tier/
    ├── Needs_Action/
    ├── Logs/
    ├── Plans/
    ├── inbox/
    ├── Done/
    └── skills/
```

---

## 🔄 COMPLETE WORKFLOW EXAMPLE

### Facebook Post Request:

**Step 1: needs_action**
```markdown
File: Needs_Action/facebook_post_request.md

# Facebook Post Request

**Requested by:** Naz Sheikh
**Date:** 2026-03-28
**Priority:** Normal

**Content:**
Post about new business update

**Platform:** Facebook
**Schedule:** ASAP
```

**Step 2: logs**
```markdown
File: Logs/facebook_20260328.log

[2026-03-28 10:00:00] Received post request
[2026-03-28 10:01:00] Generating post content
[2026-03-28 10:02:00] Content generated
[2026-03-28 10:03:00] Moving to plans
```

**Step 3: plans**
```markdown
File: Plans/facebook_post_plan.md

# Facebook Post Plan

**Original Request:** facebook_post_request.md
**Status:** Planning

**Plan:**
1. Generate engaging content
2. Add emojis and hashtags
3. Schedule for optimal time
4. Submit for approval

**Generated Content:**
🌟 Exciting business update coming soon!
Stay tuned for amazing news from Gold Tier!
#GoldTier #Business #Success
```

**Step 4: inbox/approve**
```markdown
File: inbox/facebook_post_approval.md

# Approval Required

**Type:** Facebook Post
**Status:** Awaiting Approval

**Content:**
🌟 Exciting business update coming soon!

**Actions:**
- [ ] Approve
- [ ] Edit
- [ ] Reject

**Approved by:** ___________
**Date:** ___________
```

**Step 5: done**
```markdown
File: Done/facebook_post_20260328.md

# Facebook Post - COMPLETED

**Original Request:** facebook_post_request.md
**Completed:** 2026-03-28 14:30:00

**Posted Content:**
🌟 Exciting business update coming soon!

**Post ID:** 123456789
**Link:** https://facebook.com/p/123456789

**Status:** ✅ Published
```

---

## 🚀 RUNNING THE SYSTEM

### Start All Watchers:
```bash
python AI_Employee_Vault/complete_workflow.py start all
```

### Check Status:
```bash
python AI_Employee_Vault/complete_workflow.py status
```

### Process needs_action:
```bash
python AI_Employee_Vault/process_needs_with_approval.py
```

---

**Complete workflow system ready!** 🎉
