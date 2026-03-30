# Facebook/Instagram Token Lene Ka Aasaan Tareeka
# فیس بک/انسٹاگرام ٹوکن لینے کا آسان طریقہ

## Method 1: Meta Business Suite (Sab Se Aasaan)

### Step 1: Business Suite Kholain
```
https://business.facebook.com
```

### Step 2: Settings Mein Jaayein
```
1. Left menu mein "Settings" click karein
2. "Business Settings" select karein
```

### Step 3: System Users
```
1. Left menu: Users → System Users
2. "Add" button click karein
3. Name: "Gold Tier MCP"
4. Click "Create System User"
```

### Step 4: Assets Assign Karein
```
1. Naya banaya hua System User select karein
2. "Add Assets" click karein
3. "Pages" select karein
4. Apna "Gold Tier" page select karein
5. Permissions: "Full Control" dein
6. "Save Changes" dabayein
```

### Step 5: Token Generate Karein
```
1. System User abhi bhi select ho
2. "Generate New Token" click karein
3. "Select Asset" → "Pages" choose karein
4. Page: "Gold Tier" select karein
5. Permissions select karein:
   ✓ manage_pages
   ✓ pages_show_list
   ✓ pages_read_engagement
   ✓ pages_manage_posts
   ✓ read_insights
6. "Generate Token" dabayein
7. Token copy kar lein! (Yeh aap ka Facebook Access Token hai)
```

---

## Method 2: Graph API Explorer (Direct Link)

### Direct Link:
```
https://developers.facebook.com/tools/explorer/
```

### Steps:
```
1. Upar di gayi link kholain
2. Login karein (Naz Sheikh account)
3. "Generate Access Token" button click karein
4. Permissions window khulegi
5. Ye permissions select karein:
   ✓ pages_show_list
   ✓ pages_read_engagement
   ✓ pages_manage_posts
   ✓ instagram_basic
   ✓ instagram_content_publish
6. "Continue" → "Done" dabayein
7. Ab box mein likhein: /me/accounts
8. "Submit" dabayein
9. Response mein "access_token" copy kar lein
```

---

## Method 3: Instagram Business ID Kaise Lein

### Graph API Explorer Mein:
```
1. Wahi upar wali link kholain
2. Apna token select karein
3. Box mein likhein:
   GET /me/accounts?fields=instagram_business_account
4. "Submit" dabayein
5. Response mein Instagram Business ID copy kar lein
```

---

## Method 4: Agar Token Nahi Mil Raha (Temporary Solution)

### Test Mode Mein Chalayein:

Facebook aur Instagram MCP servers **bina token ke bhi test mode** mein chal sakte hain.

`.env` file mein ye likhein:

```
# Facebook (Test Mode)
FACEBOOK_PAGE_ACCESS_TOKEN=test_token_will_use_mock_data
FACEBOOK_PAGE_ID=956241877582673
PORT=3000

# Instagram (Test Mode)
INSTAGRAM_BUSINESS_ID=test_instagram_id
INSTAGRAM_ACCESS_TOKEN=test_token_will_use_mock_data
PORT=3001
```

**Note:** Test mode mein sirf health check kaam karegi, actual posts nahi honge.

---

## Method 5: MCP Client Se Direct Integration

Agar aap MCP client (Claude Desktop, etc.) use kar rahi hain, toh:

### Claude Desktop Config:

```json
{
  "mcpServers": {
    "facebook": {
      "command": "node",
      "args": ["C:\\Users\\AA\\Desktop\\gold_tier\\facebook_mcp.js"],
      "env": {
        "FACEBOOK_PAGE_ACCESS_TOKEN": "YOUR_TOKEN_HERE",
        "FACEBOOK_PAGE_ID": "956241877582673"
      }
    },
    "instagram": {
      "command": "node",
      "args": ["C:\\Users\\AA\\Desktop\\gold_tier\\instagram_mcp.js"],
      "env": {
        "INSTAGRAM_BUSINESS_ID": "YOUR_ID_HERE",
        "INSTAGRAM_ACCESS_TOKEN": "YOUR_TOKEN_HERE"
      }
    }
  }
}
```

---

## Quick Links

| Service | Direct Link |
|---------|-------------|
| Meta Business Suite | https://business.facebook.com |
| Graph API Explorer | https://developers.facebook.com/tools/explorer/ |
| Facebook Page | https://www.facebook.com/956241877582673 |
| Instagram Account | https://www.instagram.com |

---

## Agar Abhi Bhi Masla Ho:

### WhatsApp Pe Contact Karein:
```
Facebook/Meta Support:
https://www.facebook.com/help/contact/
```

### Video Tutorial:
```
YouTube: "How to get Facebook Page Access Token 2026"
```

---

## Test Karein:

Token milne ke baad test karein:

```bash
# Browser mein ye link kholain:
http://localhost:3000/health

# Facebook MCP test:
http://localhost:3000/api/page/info

# Instagram MCP test:
http://localhost:3001/health
```

---

**Last Try:** Pehle **Method 1** try karein (Meta Business Suite), woh sab se aasaan hai!
