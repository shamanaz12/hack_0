/**
 * Facebook MCP Server
 * Connects to Facebook Graph API for page management
 * 
 * Setup Instructions:
 * 1. Copy .env.facebook to .env
 * 2. Fill in your App ID, App Secret, and Page Access Token
 * 3. Run: node facebook_mcp.js
 */

require('dotenv').config();
const express = require('express');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3000;

// Facebook Graph API Configuration
const GRAPH_API_VERSION = 'v18.0';
const BASE_URL = `https://graph.facebook.com/${GRAPH_API_VERSION}`;

// Your Facebook App Credentials
const APP_ID = process.env.FACEBOOK_APP_ID;
const APP_SECRET = process.env.FACEBOOK_APP_SECRET;
const PAGE_ACCESS_TOKEN = process.env.FACEBOOK_PAGE_ACCESS_TOKEN;
const PAGE_ID = process.env.FACEBOOK_PAGE_ID;

// Middleware
app.use(express.json());

// Health Check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', message: 'Facebook MCP Server is running' });
});

// Get Page Info
app.get('/api/page/info', async (req, res) => {
    try {
        const response = await axios.get(`${BASE_URL}/${PAGE_ID}`, {
            params: {
                fields: 'id,name,about,category,followers_count,likes,website,phone,email',
                access_token: PAGE_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching page info:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Page Posts
app.get('/api/page/posts', async (req, res) => {
    try {
        const response = await axios.get(`${BASE_URL}/${PAGE_ID}/posts`, {
            params: {
                fields: 'id,message,created_time,likes.summary(true),comments.summary(true),shares',
                limit: req.query.limit || 10,
                access_token: PAGE_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching posts:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Create New Post
app.post('/api/page/post', async (req, res) => {
    try {
        const { message, link, picture } = req.body;
        
        const response = await axios.post(`${BASE_URL}/${PAGE_ID}/feed`, {
            message,
            link,
            picture,
            access_token: PAGE_ACCESS_TOKEN
        });
        
        res.json({ success: true, post_id: response.data.id });
    } catch (error) {
        console.error('Error creating post:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Page Insights (Analytics)
app.get('/api/page/insights', async (req, res) => {
    try {
        const response = await axios.get(`${BASE_URL}/${PAGE_ID}/insights`, {
            params: {
                metric: 'page_impressions,page_engaged_users,page_post_engagements,page_likes',
                period: 'day',
                access_token: PAGE_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching insights:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get Comments on Post
app.get('/api/post/:postId/comments', async (req, res) => {
    try {
        const { postId } = req.params;
        const response = await axios.get(`${BASE_URL}/${postId}/comments`, {
            params: {
                fields: 'id,from,message,created_time,like_count',
                access_token: PAGE_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching comments:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Reply to Comment
app.post('/api/comment/:commentId/reply', async (req, res) => {
    try {
        const { commentId } = req.params;
        const { message } = req.body;
        
        const response = await axios.post(`${BASE_URL}/${commentId}/feed`, {
            message,
            access_token: PAGE_ACCESS_TOKEN
        });
        
        res.json({ success: true, reply_id: response.data.id });
    } catch (error) {
        console.error('Error replying to comment:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Get User's Pages List
app.get('/api/user/pages', async (req, res) => {
    try {
        const response = await axios.get(`${BASE_URL}/me/accounts`, {
            params: {
                access_token: PAGE_ACCESS_TOKEN
            }
        });
        res.json(response.data);
    } catch (error) {
        console.error('Error fetching pages:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Delete Post
app.delete('/api/post/:postId', async (req, res) => {
    try {
        const { postId } = req.params;
        await axios.delete(`${BASE_URL}/${postId}`, {
            params: {
                access_token: PAGE_ACCESS_TOKEN
            }
        });
        res.json({ success: true, message: 'Post deleted successfully' });
    } catch (error) {
        console.error('Error deleting post:', error.response?.data || error.message);
        res.status(500).json({ error: error.response?.data || error.message });
    }
});

// Upload Photo to Page
app.post('/api/page/photo', async (req, res) => {
    try {
        const { url, caption } = req.body;
        
        const response = await axios.post(`${BASE_URL}/${PAGE_ID}/photos`, {
            url,
            caption,
            access_token: PAGE_ACCESS_TOKEN
        });
        
        res.json({ success: true, photo_id: response.data.id });
    } catch (error) {
        console.error('Error uploading photo:', error.response?.data || error.message);
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
║           Facebook MCP Server Started                  ║
╠════════════════════════════════════════════════════════╣
║  Port: ${PORT}                                        
║  Graph API Version: ${GRAPH_API_VERSION}               
║  Page ID: ${PAGE_ID || 'Not configured'}               
║                                                        
║  Endpoints:                                            
║  GET  /health              - Health check              
║  GET  /api/page/info       - Get page information      
║  GET  /api/page/posts      - Get page posts            
║  POST /api/page/post       - Create new post           
║  GET  /api/page/insights   - Get page analytics        
║  GET  /api/user/pages      - Get user's pages          
║  GET  /api/post/:id/comments - Get post comments       
║  POST /api/comment/:id/reply - Reply to comment        
║  DELETE /api/post/:id      - Delete post               
║  POST /api/page/photo      - Upload photo              
╚════════════════════════════════════════════════════════╝
    `);
});
