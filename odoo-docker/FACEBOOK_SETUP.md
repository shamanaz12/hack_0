# Facebook/Instagram MCP Server Setup Guide

## Overview

This MCP server connects to Facebook Graph API to post on Facebook Pages and Instagram Business accounts.

## Prerequisites

- Python 3.8+
- Facebook Developer Account
- Facebook Page (with admin access)
- Instagram Business Account (connected to Facebook Page)

---

## Step 1: Create a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **My Apps** → **Create App**
3. Select **Business** as the app type
4. Fill in:
   - **App Name**: e.g., "Social Media MCP Server"
   - **App Contact Email**: your email
5. Click **Create App**

---

## Step 2: Add Facebook Login Product

1. In your App Dashboard, find **Facebook Login** product
2. Click **Set Up**
3. Select **Web** as the platform
4. Configure settings (you can use `http://localhost` for local development)

---

## Step 3: Get Page Access Token

### Option A: Using Graph API Explorer (Recommended for Testing)

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Click **Get Token** → **Get Page Access Token**
4. Select your Page
5. Add permissions:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_show_list`
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_user_content`
6. Click **Generate Access Token**
7. Copy the token

### Option B: Get Long-Lived Page Access Token

1. First get a short-lived user token from Graph API Explorer
2. Exchange for long-lived user token:
   ```
   GET https://graph.facebook.com/v18.0/oauth/access_token?
       grant_type=fb_exchange_token&
       client_id={app-id}&
       client_secret={app-secret}&
       fb_exchange_token={short-lived-token}
   ```
3. Get Page token from long-lived user token:
   ```
   GET https://graph.facebook.com/v18.0/me/accounts?
       access_token={long-lived-user-token}
   ```
4. Copy the `access_token` from your Page in the response

---

## Step 4: Get Instagram Account ID

1. In Graph API Explorer, make this request:
   ```
   GET /{page-id}?fields=instagram_business_account&access_token={access-token}
   ```
2. Copy the `id` from `instagram_business_account`

Or use this endpoint to get Instagram account details:
```
GET /{page-id}/instagram_business_account?access_token={access-token}
```

---

## Step 5: Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
FACEBOOK_ACCESS_TOKEN=your-long-lived-page-access-token
FACEBOOK_PAGE_ID=your-page-id
INSTAGRAM_ACCOUNT_ID=your-instagram-business-account-id
```

---

## Step 6: Install Dependencies

```bash
pip install mcp
```

---

## Step 7: Run the Server

```bash
python facebook_mcp_server.py
```

---

## Step 8: Test the Server

### Using the Test Client

```bash
python test_facebook_client.py
```

### Using Python Code

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio

async def test():
    server_params = StdioServerParameters(
        command="python",
        args=["facebook_mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Verify token
            result = await session.call_tool("verify_facebook_token", {})
            print(result[0].text)
            
            # Post to Facebook
            result = await session.call_tool("post_to_facebook", {
                "message": "Hello from MCP!",
                "image_url": "https://example.com/image.jpg"
            })
            print(result[0].text)

asyncio.run(test())
```

---

## Available Tools

### 1. post_to_facebook

Post to Facebook Page.

**Parameters:**
- `message` (required): Post content
- `image_url` (optional): Image/link to include

**Example:**
```json
{
  "message": "Check out our new product!",
  "image_url": "https://example.com/product.jpg"
}
```

### 2. post_to_instagram

Post to Instagram Business account.

**Parameters:**
- `message` (required): Caption
- `image_url` (required): Image URL

**Example:**
```json
{
  "message": "Beautiful sunset! #nature",
  "image_url": "https://example.com/sunset.jpg"
}
```

### 3. get_facebook_page_insights

Get Page analytics and metrics.

**Parameters:** None

**Returns:** Reach, impressions, engagement, likes, followers, etc.

### 4. verify_facebook_token

Verify the access token is valid.

**Parameters:** None

---

## Troubleshooting

### "Invalid OAuth Access Token"

- Token may have expired. Get a new long-lived token.
- Ensure you're using a Page Access Token, not a User Token.

### "Permissions Missing"

Add these permissions in App Review:
- `pages_manage_posts`
- `pages_read_engagement`
- `instagram_basic`
- `instagram_content_publish`

### "Instagram Account Not Found"

- Ensure Instagram is a Business account
- Ensure Instagram is connected to your Facebook Page
- Get the correct Instagram Account ID using Step 4

### "Media Upload Failed"

- Image URL must be publicly accessible
- Image must meet Instagram requirements (aspect ratio, size)
- For videos, use `.mp4` format

---

## Token Expiration

- **Short-lived tokens**: ~1 hour
- **Long-lived tokens**: ~60 days

Set a reminder to refresh your token every 2 months, or implement token refresh logic.

---

## App Review for Production

Before going live, submit your app for review:

1. Go to App Dashboard → **App Review**
2. Submit each permission for review
3. Provide screencast showing how you use each permission
4. Wait for approval (typically 1-7 days)

---

## References

- [Facebook Graph API Docs](https://developers.facebook.com/docs/graph-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Access Token Guide](https://developers.facebook.com/docs/facebook-login/guides/access-tokens)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
