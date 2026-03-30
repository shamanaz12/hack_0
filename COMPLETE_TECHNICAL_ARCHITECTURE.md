# Gold Tier - Complete Technical Architecture

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI LAYER (Qwen/Dashscope)                    │
│  - Natural Language Processing                                  │
│  - Content Generation                                           │
│  - Decision Making                                              │
│  - Image Recognition                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MCP SERVER LAYER                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Gmail    │ │ WhatsApp │ │ Calendar │ │ Slack    │          │
│  │ MCP      │ │ MCP      │ │ MCP      │ │ MCP      │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ Facebook │ │Instagram │ │  Odoo    │ │  Twitter │          │
│  │ MCP      │ │ MCP      │ │  MCP     │ │  MCP     │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    TOOLS LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Playwright   │  │ SMTP/IMAP    │  │ REST APIs    │         │
│  │ (Browser)    │  │ (Email)      │  │ (Services)   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Web Scraping │  │ File System  │  │ Database     │         │
│  │ (Puppeteer)  │  │ (I/O)        │  │ (SQLite)     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW LAYER                               │
│  needs_action → logs → plans → inbox/approve → done            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 REAL IMPLEMENTATIONS (NO MOCK)

### 1. **Gmail MCP Server**
**File:** `mcp_servers/gmail_mcp_server.py`

**Tools:**
- `smtplib` - Send emails
- `imaplib` - Read emails
- `email` - Parse emails
- `playwright` - Browser automation (fallback)

**AI Integration:**
```python
from dashscope import Generation
import smtplib
from email.mime.text import MIMEText

class GmailMCP:
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.gmail_email = os.getenv('GMAIL_EMAIL')
        self.gmail_password = os.getenv('GMAIL_APP_PASSWORD')
    
    def ai_generate_email(self, prompt: str) -> str:
        """Use Qwen AI to generate email content"""
        response = Generation.call(
            model='qwen-plus',
            api_key=self.api_key,
            prompt=f"Write a professional email: {prompt}"
        )
        return response.output.text
    
    def send_email(self, to: str, subject: str, body: str):
        """Send real email via SMTP"""
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.gmail_email
        msg['To'] = to
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(self.gmail_email, self.gmail_password)
        server.send_message(msg)
        server.quit()
```

---

### 2. **WhatsApp MCP Server**
**File:** `mcp_servers/whatsapp_mcp_server.py`

**Tools:**
- `playwright` - WhatsApp Web automation
- `requests` - WhatsApp Business API
- `twilio` - Twilio API for WhatsApp

**AI Integration:**
```python
from playwright.sync_api import sync_playwright
from dashscope import Generation

class WhatsAppMCP:
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.playwright = None
        self.page = None
    
    def ai_generate_message(self, context: str) -> str:
        """Use Qwen AI to generate message"""
        response = Generation.call(
            model='qwen-plus',
            api_key=self.api_key,
            prompt=f"Write a WhatsApp message: {context}"
        )
        return response.output.text
    
    def send_message_browser(self, phone: str, message: str):
        """Send WhatsApp message via browser automation"""
        if not self.page:
            self.playwright = sync_playwright().start()
            browser = self.playwright.chromium.launch()
            self.page = browser.new_page()
            self.page.goto('https://web.whatsapp.com')
            input("Scan QR code and press Enter...")
        
        # Navigate to chat
        self.page.goto(f'https://web.whatsapp.com/send?phone={phone}')
        time.sleep(3)
        
        # Type and send message
        self.page.type('div[contenteditable="true"]', message)
        self.page.keyboard.press('Enter')
```

---

### 3. **Facebook MCP Server**
**File:** `mcp_servers/facebook_mcp_playwright.py`

**Tools:**
- `playwright` - Facebook automation
- `requests` - Graph API (optional)

**AI Integration:**
```python
from dashscope import Generation
from playwright.sync_api import sync_playwright

class FacebookMCP:
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.email = os.getenv('FACEBOOK_EMAIL')
        self.password = os.getenv('FACEBOOK_PASSWORD')
    
    def ai_generate_post(self, topic: str) -> str:
        """Use Qwen AI to generate post"""
        response = Generation.call(
            model='qwen-plus',
            api_key=self.api_key,
            prompt=f"Write an engaging Facebook post about: {topic}"
        )
        return response.output.text
    
    def post_to_facebook(self, message: str):
        """Post to Facebook via browser automation"""
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Login
        page.goto('https://facebook.com/login')
        page.fill('#email', self.email)
        page.fill('#pass', self.password)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        
        # Create post
        page.goto('https://facebook.com')
        page.click('[data-testid="create_post"]')
        page.fill('div[role="textbox"]', message)
        page.click('button:has-text("Post")')
```

---

### 4. **Instagram MCP Server**
**File:** `mcp_servers/instagram_mcp_playwright.py`

**Tools:**
- `playwright` - Instagram automation
- `instagrapi` - Instagram API library

**AI Integration:**
```python
from dashscope import Generation
from instagrapi import Client

class InstagramMCP:
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.client = Client()
    
    def ai_generate_caption(self, image_description: str) -> str:
        """Use Qwen AI to generate caption"""
        response = Generation.call(
            model='qwen-plus',
            api_key=self.api_key,
            prompt=f"Write an Instagram caption for: {image_description}"
        )
        return response.output.text
    
    def post_photo(self, image_path: str, caption: str):
        """Post photo to Instagram"""
        self.client.login(self.username, self.password)
        self.client.photo_upload(image_path, caption)
```

---

### 5. **Calendar MCP Server**
**File:** `mcp_servers/calendar_mcp_server.py`

**Tools:**
- `google-api-python-client` - Google Calendar API
- `icalendar` - iCalendar format
- `playwright` - Browser automation (fallback)

**AI Integration:**
```python
from dashscope import Generation
from googleapiclient.discovery import build

class CalendarMCP:
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.credentials = self._load_credentials()
    
    def ai_parse_event_request(self, text: str) -> dict:
        """Use Qwen AI to parse event details from text"""
        response = Generation.call(
            model='qwen-plus',
            api_key=self.api_key,
            prompt=f"Extract event details: {text}"
        )
        # Returns: {title, start_time, end_time, attendees}
        return json.loads(response.output.text)
    
    def create_event(self, event_data: dict):
        """Create Google Calendar event"""
        service = build('calendar', 'v3', credentials=self.credentials)
        event = service.events().insert(
            calendarId='primary',
            body=event_data
        ).execute()
        return event
```

---

### 6. **Slack MCP Server**
**File:** `mcp_servers/slack_mcp_server.py`

**Tools:**
- `slack-sdk` - Slack Web API
- `playwright` - Browser automation (fallback)

**AI Integration:**
```python
from dashscope import Generation
from slack_sdk import WebClient

class SlackMCP:
    def __init__(self):
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        self.client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
    
    def ai_generate_message(self, context: str) -> str:
        """Use Qwen AI to generate Slack message"""
        response = Generation.call(
            model='qwen-plus',
            api_key=self.api_key,
            prompt=f"Write a Slack message: {context}"
        )
        return response.output.text
    
    def send_message(self, channel: str, message: str):
        """Send Slack message"""
        self.client.chat_postMessage(
            channel=channel,
            text=message
        )
```

---

## 🔄 COMPLETE WORKFLOW EXAMPLE

### User Request: "Send email to Shama about meeting"

**Step 1: needs_action**
```markdown
# Email Request

Send meeting invitation to Shama
Topic: Project discussion
Time: Tomorrow 3 PM
```

**Step 2: AI Processing**
```python
# AI generates email content
ai_content = ai_generate_email("Meeting invitation to Shama, tomorrow 3 PM, project discussion")

# Result:
"""
Subject: Project Discussion Meeting - Tomorrow 3 PM

Dear Shama,

I hope this email finds you well. I would like to schedule a meeting 
to discuss our ongoing project...

Best regards,
Gold Tier Team
"""
```

**Step 3: logs**
```markdown
# Email Log

- AI generated content: ✅
- Recipient: shama@example.com
- Subject: Project Discussion Meeting
- Status: Awaiting approval
```

**Step 4: plans**
```markdown
# Email Plan

1. ✅ Parse request
2. ✅ Generate content with AI
3. ⏳ Submit for approval
4. ⏳ Send via SMTP
5. ⏳ Mark as done
```

**Step 5: inbox/approve**
```markdown
# Approval Required

**To:** shama@example.com
**Subject:** Project Discussion Meeting
**Content:** [AI generated content]

[ ] Approve  [ ] Edit  [ ] Reject
```

**Step 6: done**
```markdown
# Email Sent - COMPLETED

**Sent:** 2026-03-28 15:30:00
**Message ID:** <abc123@gmail.com>
**Status:** ✅ Delivered
```

---

## 📋 IMPLEMENTATION CHECKLIST

| MCP Server | AI Integration | Tools | Status |
|------------|---------------|-------|--------|
| Gmail | ✅ Qwen AI | SMTP, IMAP, Playwright | ⏳ Create |
| WhatsApp | ✅ Qwen AI | Playwright, Twilio API | ⏳ Create |
| Facebook | ✅ Qwen AI | Playwright, Graph API | ⏳ Create |
| Instagram | ✅ Qwen AI | instagrapi, Playwright | ⏳ Create |
| Calendar | ✅ Qwen AI | Google API, Playwright | ⏳ Create |
| Slack | ✅ Qwen AI | Slack SDK | ⏳ Create |
| Odoo | ✅ Qwen AI | XML-RPC | ✅ Exists |

---

**This is the REAL architecture - NO MOCK, pure AI + Tools integration!** 🚀
