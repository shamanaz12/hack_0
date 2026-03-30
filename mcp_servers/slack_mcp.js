/**
 * Slack MCP Server
 * Gold Tier - Slack Integration
 * 
 * Features:
 * - Send messages
 * - Read channels
 * - Send DMs
 * - Upload files
 * - Get channel history
 * 
 * Usage:
 *   node slack_mcp.js
 *   node slack_mcp.js --test
 */

const express = require('express');
const { WebClient } = require('@slack/web-api');
const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

// Load environment
dotenv.config();

// Configuration
const PORT = process.env.SLACK_PORT || 3003;
const SLACK_BOT_TOKEN = process.env.SLACK_BOT_TOKEN || '';
const SLACK_SIGNING_SECRET = process.env.SLACK_SIGNING_SECRET || '';

// Initialize Slack client
const slackClient = new WebClient(SLACK_BOT_TOKEN);

// Express app
const app = express();
app.use(express.json());

// MCP Server info
const mcp_info = {
  name: 'Slack MCP',
  version: '1.0.0',
  description: 'Gold Tier Slack Integration',
  features: [
    'send_message',
    'read_channel',
    'send_dm',
    'upload_file',
    'get_history',
    'list_channels'
  ]
};

// ============== API ENDPOINTS ==============

/**
 * Health Check
 */
app.get('/health', async (req, res) => {
  try {
    const auth = await slackClient.auth.test();
    res.json({
      status: 'healthy',
      team: auth.team,
      user: auth.user,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(500).json({
      status: 'unhealthy',
      error: error.message
    });
  }
});

/**
 * Send Message to Channel
 * POST /api/slack/message
 * Body: { channel, text }
 */
app.post('/api/slack/message', async (req, res) => {
  try {
    const { channel, text } = req.body;
    
    if (!channel || !text) {
      return res.status(400).json({
        success: false,
        error: 'Channel and text are required'
      });
    }
    
    const result = await slackClient.chat.postMessage({
      channel: channel,
      text: text
    });
    
    res.json({
      success: true,
      message_id: result.ts,
      channel: result.channel,
      permalink: result.permalink,
      message: 'Message sent successfully'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Send Direct Message
 * POST /api/slack/dm
 * Body: { userId, text }
 */
app.post('/api/slack/dm', async (req, res) => {
  try {
    const { userId, text } = req.body;
    
    if (!userId || !text) {
      return res.status(400).json({
        success: false,
        error: 'UserId and text are required'
      });
    }
    
    // Open DM conversation
    const im = await slackClient.conversations.open({
      users: userId
    });
    
    // Send message
    const result = await slackClient.chat.postMessage({
      channel: im.channel.id,
      text: text
    });
    
    res.json({
      success: true,
      message_id: result.ts,
      channel: result.channel,
      permalink: result.permalink,
      message: 'DM sent successfully'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Read Channel Messages
 * GET /api/slack/channel/:channelId/history?limit=10
 */
app.get('/api/slack/channel/:channelId/history', async (req, res) => {
  try {
    const { channelId } = req.params;
    const { limit = 10 } = req.query;
    
    const result = await slackClient.conversations.history({
      channel: channelId,
      limit: parseInt(limit)
    });
    
    res.json({
      success: true,
      messages: result.messages.map(msg => ({
        ts: msg.ts,
        user: msg.user,
        text: msg.text,
        timestamp: new Date(parseFloat(msg.ts) * 1000).toISOString()
      })),
      count: result.messages.length,
      has_more: result.has_more
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * List Channels
 * GET /api/slack/channels
 */
app.get('/api/slack/channels', async (req, res) => {
  try {
    const result = await slackClient.conversations.list({
      types: 'public_channel,private_channel'
    });
    
    res.json({
      success: true,
      channels: result.channels.map(channel => ({
        id: channel.id,
        name: channel.name,
        purpose: channel.purpose?.value || '',
        topic: channel.topic?.value || '',
        num_members: channel.num_members,
        is_private: channel.is_private
      })),
      count: result.channels.length
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Upload File
 * POST /api/slack/upload
 * Body: { channel, file_path, title, initial_comment }
 */
app.post('/api/slack/upload', async (req, res) => {
  try {
    const { channel, file_path, title, initial_comment } = req.body;
    
    if (!channel || !file_path) {
      return res.status(400).json({
        success: false,
        error: 'Channel and file_path are required'
      });
    }
    
    const result = await slackClient.files.upload({
      channels: channel,
      file: fs.createReadStream(file_path),
      title: title || path.basename(file_path),
      initial_comment: initial_comment || ''
    });
    
    res.json({
      success: true,
      file_id: result.file.id,
      permalink: result.file.permalink,
      message: 'File uploaded successfully'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get Channel Info
 * GET /api/slack/channel/:channelId
 */
app.get('/api/slack/channel/:channelId', async (req, res) => {
  try {
    const { channelId } = req.params;
    
    const result = await slackClient.conversations.info({
      channel: channelId
    });
    
    res.json({
      success: true,
      channel: {
        id: result.channel.id,
        name: result.channel.name,
        purpose: result.channel.purpose?.value || '',
        topic: result.channel.topic?.value || '',
        num_members: result.channel.num_members,
        created: new Date(result.channel.created * 1000).toISOString(),
        creator: result.channel.creator
      }
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * MCP Info
 */
app.get('/api/mcp/info', (req, res) => {
  res.json(mcp_info);
});

// ============== START SERVER ==============

if (require.main === module) {
  app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('   SLACK MCP SERVER');
    console.log('='.repeat(60));
    console.log(`   Port: http://localhost:${PORT}`);
    console.log(`   Token Configured: ${SLACK_BOT_TOKEN ? 'Yes' : 'No'}`);
    console.log('='.repeat(60));
    console.log();
    console.log('   Endpoints:');
    console.log('   GET  /health - Health check');
    console.log('   POST /api/slack/message - Send message');
    console.log('   POST /api/slack/dm - Send DM');
    console.log('   GET  /api/slack/channels - List channels');
    console.log('   GET  /api/slack/channel/:id - Get channel info');
    console.log('   GET  /api/slack/channel/:id/history - Get messages');
    console.log('   POST /api/slack/upload - Upload file');
    console.log('   GET  /api/mcp/info - MCP info');
    console.log();
    console.log('='.repeat(60));
    
    // Open browser
    const open = require('open');
    open(`http://localhost:${PORT}/api/mcp/info`);
  });
}

module.exports = app;
