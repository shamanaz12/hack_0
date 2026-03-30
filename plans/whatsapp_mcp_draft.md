# WhatsApp MCP Server - Draft

## Overview
Gold Tier WhatsApp integration for messaging and communication.

## Features
- ✅ Send text messages
- ✅ Send template messages
- ✅ Send media (images/documents)
- ✅ Get contacts
- ✅ Message history
- ✅ Webhook support (incoming messages)

## Setup Instructions

### 1. Create WhatsApp Business App
1. Go to: https://developers.facebook.com/
2. Create new app
3. Add "WhatsApp" product
4. Complete business verification

### 2. Get Credentials
1. Go to WhatsApp > API Setup
2. Copy Phone Number ID
3. Copy Access Token (temporary)
4. For production: Generate permanent token

### 3. Configure .env
```env
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_API_URL=https://graph.facebook.com/v17.0
WHATSAPP_PORT=3004
```

## API Endpoints

### Health Check
```
GET /health
```

### Send Text Message
```
POST /api/whatsapp/message
Body: {
  "to": "+923161129505",
  "message": "Hello from Gold Tier!"
}
```

### Send Template Message
```
POST /api/whatsapp/template
Body: {
  "to": "+923161129505",
  "template_name": "hello_world",
  "language": "en",
  "components": []
}
```

### Send Media
```
POST /api/whatsapp/media
Body: {
  "to": "+923161129505",
  "media_url": "https://example.com/image.jpg",
  "caption": "Check this out!",
  "type": "image"
}
```

### Get Contacts
```
GET /api/whatsapp/contacts
```

### Get Message History
```
GET /api/whatsapp/messages?limit=10
```

## Usage Examples

### Start Server
```bash
node mcp_servers/whatsapp_mcp.js
```

### Test with curl
```bash
# Health check
curl http://localhost:3004/health

# Send message
curl -X POST http://localhost:3004/api/whatsapp/message \
  -H "Content-Type: application/json" \
  -d "{\"to\":\"+923161129505\",\"message\":\"Hello from Gold Tier!\"}"

# Get contacts
curl http://localhost:3004/api/whatsapp/contacts
```

## Template Messages

WhatsApp requires pre-approved templates for business-initiated conversations.

### Create Template:
1. Go to WhatsApp Manager
2. Message Templates > Create
3. Fill in template content
4. Submit for approval
5. Once approved, use in API

### Example Template:
```json
{
  "name": "order_confirmation",
  "language": "en",
  "components": [
    {
      "type": "body",
      "parameters": [
        {
          "type": "text",
          "text": "Order #12345"
        }
      ]
    }
  ]
}
```

## Integration with Gold Tier
- Part of MCP server network
- Works with orchestrator
- Supports autonomous notifications
- Can send alerts and updates

## Next Steps
1. Create WhatsApp Business app
2. Get phone number verified
3. Configure credentials
4. Test API endpoints
5. Create message templates
6. Integrate with Gold Tier
