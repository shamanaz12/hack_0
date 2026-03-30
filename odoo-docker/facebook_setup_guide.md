# Facebook MCP Server Setup Guide
# فیس بوک ایم سی پی سرور سیٹ اپ گائیڈ

## Complete Setup Instructions | مکمل سیٹ اپ کی ہدایات

---

## Part 1: Get Facebook App Credentials
## حصہ 1: فیس بوک ایپ کی اسناد حاصل کریں

### Step 1: Open Meta Business Suite
```
1. Go to: https://business.facebook.com
2. Select your business: "Gold Tier"
3. Click on "Settings" (gear icon ⚙️)
```

### Step 2: Create Facebook App
```
1. In Business Settings, go to: Accounts → Apps
2. Click "Add" → "Create a New App"
3. App Type: Select "Business"
4. App Name: "Facebook MCP Server"
5. Business: Select "Gold Tier"
6. Click "Create App"
```

### Step 3: Get App ID and App Secret
```
1. In App Dashboard, go to: Settings → Basic
2. Copy "App ID" (save for later)
3. Click "Show" next to "App Secret" and copy it (save securely)
```

### Step 4: Configure Facebook Login
```
1. In App Dashboard, click "Add Product"
2. Find "Facebook Login" → Click "Set Up"
3. Go to: Facebook Login → Settings
4. Add Valid OAuth Redirect URI: http://localhost:3000/auth/callback
5. Enable "Client OAuth Login": ON
6. Enable "Embedded Browser OAuth Login": ON
7. Click "Save Changes"
```

### Step 5: Switch App to Live Mode
```
1. In App Dashboard, look for toggle at top
2. Change from "Development" to "Live"
3. Confirm the change
```

---

## Part 2: Get Page Access Token
## حصہ 2: پیج ایکسیس ٹوکن حاصل کریں

### Step 1: Open Graph API Explorer
```
1. Go to: https://developers.facebook.com/tools/explorer/
2. From dropdown, select your app: "Facebook MCP Server"
```

### Step 2: Generate Access Token
```
1. Click "Generate Access Token" button
2. A popup will show permissions
```

### Step 3: Select Required Permissions
Select these 6 permissions:
```
✓ pages_show_list
✓ pages_read_engagement
✓ pages_read_user_content
✓ pages_manage_posts
✓ pages_manage_engagement
✓ business_management
```

Click "Continue" → "Done"

### Step 4: Get Your Page Token
```
1. In Graph Explorer, run this query:
   GET /me/accounts

2. You'll see response like:
   {
     "data": [
       {
         "name": "Gold Tier",
         "id": "123456789012345",
         "access_token": "EAAGm0P4ZCqo0BOxxxxx..."
       }
     ]
   }

3. Copy the "access_token" value (this is your PAGE ACCESS TOKEN)
4. Copy the "id" value (this is your PAGE ID)
```

---

## Part 3: Configure MCP Server
## حصہ 3: ایم سی پی سرور کو ترتیب دیں

### Step 1: Install Dependencies
```bash
cd C:\Users\AA\Desktop\gold_tier
npm install express axios dotenv
```

### Step 2: Create .env File
```bash
# Copy the template
copy .env.facebook .env
```

### Step 3: Fill in .env File
Open `.env` file and add your values:
```
FACEBOOK_APP_ID=123456789012345
FACEBOOK_APP_SECRET=abc123def456ghi789jkl012mno345pq
FACEBOOK_PAGE_ACCESS_TOKEN=EAAGm0P4ZCqo0BOxxxxx...
FACEBOOK_PAGE_ID=123456789012345
PORT=3000
```

### Step 4: Start the Server
```bash
node facebook_mcp.js
```

You should see:
```
╔════════════════════════════════════════════════════════╗
║           Facebook MCP Server Started                  ║
╠════════════════════════════════════════════════════════╣
║  Port: 3000
║  Graph API Version: v18.0
║  ...
╚════════════════════════════════════════════════════════╝
```

---

## Part 4: Test the API
## حصہ 4: API کو ٹیسٹ کریں

### Test Endpoints (using browser or Postman):

#### 1. Health Check
```
GET http://localhost:3000/health
```

#### 2. Get Page Info
```
GET http://localhost:3000/api/page/info
```

#### 3. Get Page Posts
```
GET http://localhost:3000/api/page/posts
```

#### 4. Create New Post
```
POST http://localhost:3000/api/page/post
Content-Type: application/json

{
  "message": "Hello from Gold Tier! This is our first post via MCP Server."
}
```

#### 5. Get Page Analytics
```
GET http://localhost:3000/api/page/insights
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health check |
| GET | `/api/page/info` | Get page information |
| GET | `/api/page/posts` | Get all page posts |
| POST | `/api/page/post` | Create new post |
| GET | `/api/page/insights` | Get page analytics |
| GET | `/api/user/pages` | Get user's pages list |
| GET | `/api/post/:id/comments` | Get comments on post |
| POST | `/api/comment/:id/reply` | Reply to a comment |
| DELETE | `/api/post/:id` | Delete a post |
| POST | `/api/page/photo` | Upload photo to page |

---

## Troubleshooting | مسائل کا حل

### Problem: "Invalid Access Token"
**Solution:**
```
1. Go to Graph API Explorer
2. Generate new access token
3. Update .env file
4. Restart server
```

### Problem: "Permission Denied"
**Solution:**
```
1. Check if app is in "Live" mode
2. Verify all 6 permissions are granted
3. Re-generate access token with all permissions
```

### Problem: "Page Not Found"
**Solution:**
```
1. Verify PAGE_ID in .env is correct
2. Make sure you have admin access to the page
3. Run GET /me/accounts to confirm page ID
```

### Problem: Registration Stuck
**Solution:**
```
1. Use Meta Business Suite instead (business.facebook.com)
2. Create business account first
3. Then create app from Business Settings
```

---

## Security Notes | سیکیورٹی نوٹس

⚠️ **IMPORTANT / اہم:**
```
- Never share your App Secret with anyone
- Never commit .env file to GitHub
- Keep access tokens secure
- Rotate tokens regularly
- Use HTTPS in production
```

---

## Support | سپورٹ

For more help:
- Facebook Developers: https://developers.facebook.com
- Graph API Docs: https://developers.facebook.com/docs/graph-api
- Meta Business Help: https://www.facebook.com/business/help

---

## Quick Start Command | فوری شروعات کا کمانڈ

```bash
# Install dependencies
npm install express axios dotenv

# Copy env file
copy .env.facebook .env

# Edit .env with your credentials
# Then start server
node facebook_mcp.js

# Test it
curl http://localhost:3000/health
```

---

**Created for: Gold Tier - Naz Sheikh**
**Date: March 26, 2026**
