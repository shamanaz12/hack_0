# Slack MCP Server - Draft

## Overview
Gold Tier Slack integration for team communication and collaboration.

## Features
- ✅ Send messages to channels
- ✅ Send direct messages
- ✅ Read channel history
- ✅ List all channels
- ✅ Upload files
- ✅ Get channel info

## Setup Instructions

### 1. Create Slack App
1. Go to: https://api.slack.com/apps
2. Click "Create New App"
3. Select your workspace
4. Name: "Gold Tier MCP"

### 2. Configure Permissions
1. Go to "OAuth & Permissions"
2. Add these scopes:
   - `chat:write` - Send messages
   - `channels:read` - Read channels
   - `groups:read` - Read private channels
   - `im:write` - Send DMs
   - `files:write` - Upload files
3. Install app to workspace
4. Copy "Bot User OAuth Token"

### 3. Configure .env
```env
SLACK_BOT_TOKEN=xoxb-your_bot_token_here
SLACK_SIGNING_SECRET=your_signing_secret
SLACK_PORT=3003
```

## API Endpoints

### Health Check
```
GET /health
```

### Send Message
```
POST /api/slack/message
Body: {
  "channel": "C0123456789",
  "text": "Hello team!"
}
```

### Send DM
```
POST /api/slack/dm
Body: {
  "userId": "U0123456789",
  "text": "Hi there!"
}
```

### List Channels
```
GET /api/slack/channels
```

### Get Channel History
```
GET /api/slack/channel/:channelId/history?limit=10
```

### Upload File
```
POST /api/slack/upload
Body: {
  "channel": "C0123456789",
  "file_path": "/path/to/file.pdf",
  "title": "Document",
  "initial_comment": "Check this out!"
}
```

### Get Channel Info
```
GET /api/slack/channel/:channelId
```

## Usage Examples

### Start Server
```bash
node mcp_servers/slack_mcp.js
```

### Test with curl
```bash
# Health check
curl http://localhost:3003/health

# Send message
curl -X POST http://localhost:3003/api/slack/message \
  -H "Content-Type: application/json" \
  -d "{\"channel\":\"general\",\"text\":\"Hello from Gold Tier!\"}"

# List channels
curl http://localhost:3003/api/slack/channels

# Get channel history
curl http://localhost:3003/api/slack/channel/C0123456789/history
```

## Channel IDs
To find channel IDs:
1. Open Slack
2. Go to channel
3. Click channel name
4. View channel details
5. Copy ID (starts with C)

Or use the API:
```bash
curl http://localhost:3003/api/slack/channels
```

## Integration with Gold Tier
- Part of MCP server network
- Works with orchestrator
- Supports autonomous notifications
- Can send alerts and updates

## Next Steps
1. Create Slack app
2. Configure tokens
3. Test API endpoints
4. Integrate with Gold Tier
5. Add automated notifications
