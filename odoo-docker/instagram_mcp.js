/**
 * Instagram MCP Server
 * Connects to Instagram Graph API for business account management
 * 
 * Prerequisites:
 * 1. Instagram Business Account connected to Facebook Page
 * 2. Facebook App with Instagram Graph API permissions
 * 3. Page Access Token with instagram_basic and instagram_content_publish permissions
 * 
 * Setup Instructions:
 * 1. Copy .env.instagram to .env
 * 2. Fill in your Instagram Business ID and Access Token
 * 3. Run: node instagram_mcp.js
 */

require('dotenv').config();
const express = require('express');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3001;

// Instagram Graph API Configuration
const GRAPH_API_VERSION = 'v18.0';
const BASE_URL = `https://graph.facebook.com/${GRAPH_API_VERSION}`;

// Instagram Business Account Configuration
const INSTAGRAM_BUSINESS_ID = process.env.INSTAGRAM_BUSINESS_ID;
const INSTAGRAM_ACCESS_TOKEN = process.env.INSTAGRAM_ACCESS_TOKEN;

// Middleware
app.use(express.json());

// Health Check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', message: 'Instagram MCP Server is running' });
});

// Get Instagram Business Account Info
app.get('/api/instagram/info', async (req, res) => {
    try {
        const response = await axios.get(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}`, {
            params: {
                fields: 'id,username,name,biography,website,profile_picture_url,followers_count,follows_count,media_count',
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching Instagram info:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Instagram Media (Posts)
app.get('/api/instagram/media', async (req, res) => {
    try {
        const response = await axios.get(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}/media`, {
            params: {
                fields: 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
                limit: req.query.limit || 10,
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching media:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Single Media Details
app.get('/api/instagram/media/:mediaId', async (req, res) => {
    try {
        const { mediaId } = req.params;
        const response = await axios.get(`${BASE_URL}/${mediaId}`, {
            params: {
                fields: 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count,children',
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching media details:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Create Image Post Container
app.post('/api/instagram/create-image', async (req, res) => {
    try {
        const { image_url, caption } = req.body;

        // Step 1: Create media container
        const containerResponse = await axios.post(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}/media`, {
            image_url,
            caption,
            access_token: INSTAGRAM_ACCESS_TOKEN
        });

        const creationId = containerResponse.data.id;

        // Step 2: Publish the media
        const publishResponse = await axios.post(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}/media_publish`, {
            creation_id: creationId,
            access_token: INSTAGRAM_ACCESS_TOKEN
        });

        res.json({ 
            success: true, 
            media_id: publishResponse.data.id,
            message: 'Image post published successfully'
        });
    } catch (error) {
        console.error('Error creating image post:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Create Carousel Post Container
app.post('/api/instagram/create-carousel', async (req, res) => {
    try {
        const { children, caption } = req.body;

        // Step 1: Create carousel container
        const containerResponse = await axios.post(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}/media`, {
            media_type: 'CAROUSEL',
            children,
            caption,
            access_token: INSTAGRAM_ACCESS_TOKEN
        });

        const creationId = containerResponse.data.id;

        // Step 2: Publish the media
        const publishResponse = await axios.post(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}/media_publish`, {
            creation_id: creationId,
            access_token: INSTAGRAM_ACCESS_TOKEN
        });

        res.json({ 
            success: true, 
            media_id: publishResponse.data.id,
            message: 'Carousel post published successfully'
        });
    } catch (error) {
        console.error('Error creating carousel post:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Comments on Media
app.get('/api/instagram/media/:mediaId/comments', async (req, res) => {
    try {
        const { mediaId } = req.params;
        const response = await axios.get(`${BASE_URL}/${mediaId}/comments`, {
            params: {
                fields: 'id,from,username,text,timestamp,like_count',
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching comments:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Reply to Comment
app.post('/api/instagram/comment/:commentId/reply', async (req, res) => {
    try {
        const { commentId } = req.params;
        const { text } = req.body;

        const response = await axios.post(`${BASE_URL}/${commentId}/replies`, {
            text,
            access_token: INSTAGRAM_ACCESS_TOKEN
        });

        res.json({ success: true, reply_id: response.data.id });
    } catch (error) {
        console.error('Error replying to comment:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Hide/Unhide Comment
app.post('/api/instagram/comment/:commentId/hide', async (req, res) => {
    try {
        const { commentId } = req.params;
        const { hide } = req.body;

        const response = await axios.post(`${BASE_URL}/${commentId}`, {
            hidden: hide,
            access_token: INSTAGRAM_ACCESS_TOKEN
        });

        res.json({ success: true, hidden: hide });
    } catch (error) {
        console.error('Error hiding comment:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Insights for Account
app.get('/api/instagram/insights', async (req, res) => {
    try {
        const response = await axios.get(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}/insights`, {
            params: {
                metric: 'impressions,reach,profile_views,website_clicks,email_contacts,phone_call_clicks,text_message_clicks,get_directions_clicks,follower_count',
                period: 'day',
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching insights:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Insights for Specific Media
app.get('/api/instagram/media/:mediaId/insights', async (req, res) => {
    try {
        const { mediaId } = req.params;
        const response = await axios.get(`${BASE_URL}/${mediaId}/insights`, {
            params: {
                metric: 'impressions,reach,saved,likes,comments,shares,saves,video_views',
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching media insights:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Stories
app.get('/api/instagram/stories', async (req, res) => {
    try {
        const response = await axios.get(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}/stories`, {
            params: {
                fields: 'id,caption,media_type,media_url,permalink,timestamp,expiring_at',
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching stories:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Tagged Media
app.get('/api/instagram/tagged', async (req, res) => {
    try {
        const response = await axios.get(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}/tagged`, {
            params: {
                fields: 'id,caption,media_type,media_url,permalink,timestamp',
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching tagged media:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Search for Hashtag
app.get('/api/instagram/hashtag/:tag', async (req, res) => {
    try {
        const { tag } = req.params;
        const response = await axios.get(`${BASE_URL}/ig_hashtag_search`, {
            params: {
                q: tag,
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error searching hashtag:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Hashtag Top Media
app.get('/api/instagram/hashtag/:id/top_media', async (req, res) => {
    try {
        const { id } = req.params;
        const response = await axios.get(`${BASE_URL}/${id}/top_media`, {
            params: {
                fields: 'id,caption,media_type,like_count,comments_count',
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching hashtag top media:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Recent Media with Mentions
app.get('/api/instagram/mentioned', async (req, res) => {
    try {
        const response = await axios.get(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}/mentioned`, {
            params: {
                fields: 'id,caption,media_type,media_url,timestamp',
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching mentioned media:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Delete Media
app.delete('/api/instagram/media/:mediaId', async (req, res) => {
    try {
        const { mediaId } = req.params;
        await axios.delete(`${BASE_URL}/${mediaId}`, {
            params: {
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });
        res.json({ success: true, message: 'Media deleted successfully' });
    } catch (error) {
        console.error('Error deleting media:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Refresh Insights (for real-time data)
app.post('/api/instagram/refresh-insights', async (req, res) => {
    try {
        // Trigger insight refresh by fetching account insights
        await axios.get(`${BASE_URL}/${INSTAGRAM_BUSINESS_ID}/insights`, {
            params: {
                metric: 'impressions,reach',
                access_token: INSTAGRAM_ACCESS_TOKEN
            }
        });

        res.json({ success: true, message: 'Insights refreshed successfully' });
    } catch (error) {
        console.error('Error refreshing insights:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Error Handling Middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

// Start Server
app.listen(PORT, () => {
    console.log(`
╔════════════════════════════════════════════════════════╗
║          Instagram MCP Server Started                  ║
╠════════════════════════════════════════════════════════╣
║  Port: ${PORT}                                         
║  Graph API Version: ${GRAPH_API_VERSION}               
║  Instagram Business ID: ${INSTAGRAM_BUSINESS_ID || 'Not configured'}
║                                                        
║  Endpoints:                                            
║  GET  /health                        - Health check    
║  GET  /api/instagram/info            - Account info    
║  GET  /api/instagram/media           - Get media posts 
║  GET  /api/instagram/media/:id       - Media details   
║  POST /api/instagram/create-image    - Post image      
║  POST /api/instagram/create-carousel - Post carousel   
║  GET  /api/instagram/insights        - Account insights
║  GET  /api/instagram/media/:id/insights - Media insights
║  GET  /api/instagram/stories         - Get stories     
║  GET  /api/instagram/tagged          - Tagged media    
║  GET  /api/instagram/mentioned       - Mentioned media 
║  GET  /api/instagram/hashtag/:tag    - Search hashtag  
║  GET  /api/instagram/media/:id/comments - Get comments 
║  POST /api/instagram/comment/:id/reply - Reply comment 
║  POST /api/instagram/comment/:id/hide  - Hide comment  
║  DELETE /api/instagram/media/:id     - Delete media    
║  POST /api/instagram/refresh-insights - Refresh insights
╚════════════════════════════════════════════════════════╝
    `);
});
