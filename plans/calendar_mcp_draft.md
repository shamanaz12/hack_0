# Google Calendar MCP Server - Draft

## Overview
Gold Tier Google Calendar integration for event management.

## Features
- ✅ Create events
- ✅ Update events
- ✅ Delete events
- ✅ List events
- ✅ Get event details
- ✅ Send invitations

## Setup Instructions

### 1. Enable Google Calendar API
1. Go to: https://console.cloud.google.com/
2. Create new project or select existing
3. Enable "Google Calendar API"
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials.json

### 2. Get Refresh Token
1. Go to: https://developers.google.com/oauthplayground
2. Select "Google Calendar API v3"
3. Authorize and get refresh token
4. Copy the refresh token

### 3. Configure .env
```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REFRESH_TOKEN=your_refresh_token
GOOGLE_CALENDAR_ID=primary
CALENDAR_PORT=3002
```

## API Endpoints

### Health Check
```
GET /health
```

### Create Event
```
POST /api/calendar/events
Body: {
  "title": "Team Meeting",
  "description": "Weekly sync",
  "startTime": "2026-03-29T10:00:00",
  "endTime": "2026-03-29T11:00:00",
  "location": "Conference Room",
  "attendees": ["user@example.com"]
}
```

### Update Event
```
PUT /api/calendar/events/:eventId
Body: {
  "title": "Updated Meeting",
  "startTime": "2026-03-29T14:00:00"
}
```

### Delete Event
```
DELETE /api/calendar/events/:eventId
```

### List Events
```
GET /api/calendar/events?maxResults=10&timeMin=2026-03-28
```

### Get Event
```
GET /api/calendar/events/:eventId
```

## Usage Examples

### Start Server
```bash
node mcp_servers/calendar_mcp.js
```

### Test with curl
```bash
# Health check
curl http://localhost:3002/health

# Create event
curl -X POST http://localhost:3002/api/calendar/events \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Meeting\",\"startTime\":\"2026-03-29T10:00:00\",\"endTime\":\"2026-03-29T11:00:00\"}"

# List events
curl http://localhost:3002/api/calendar/events
```

## Integration with Gold Tier
- Part of MCP server network
- Works with orchestrator
- Supports autonomous scheduling

## Next Steps
1. Configure Google Cloud credentials
2. Test API endpoints
3. Integrate with Gold Tier orchestrator
4. Add calendar-based automation
