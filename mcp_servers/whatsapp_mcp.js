/**
 * WhatsApp MCP Server
 * Gold Tier - WhatsApp Integration
 * 
 * Features:
 * - Send messages
 * - Send media
 * - Get contacts
 * - Get chat history
 * - Webhook support
 * 
 * Usage:
 *   node whatsapp_mcp.js
 *   node whatsapp_mcp.js --test
 */

const express = require('express');
const axios = require('axios');
const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

// Load environment
dotenv.config();

// Configuration
const PORT = process.env.WHATSAPP_PORT || 3004;
const WHATSAPP_API_URL = process.env.WHATSAPP_API_URL || '';
const WHATSAPP_PHONE_NUMBER_ID = process.env.WHATSAPP_PHONE_NUMBER_ID || '';
const WHATSAPP_ACCESS_TOKEN = process.env.WHATSAPP_ACCESS_TOKEN || '';

// Express app
const app = express();
app.use(express.json());

// MCP Server info
const mcp_info = {
  name: 'WhatsApp MCP',
  version: '1.0.0',
  description: 'Gold Tier WhatsApp Integration',
  features: [
    'send_message',
    'send_template',
    'send_media',
    'get_contacts',
    'get_messages'
  ]
};

// Mock mode (if no API credentials)
const mock_mode = !WHATSAPP_ACCESS_TOKEN || WHATSAPP_ACCESS_TOKEN === 'your_whatsapp_token_here';

if (mock_mode) {
  console.log("⚠️  WhatsApp MCP running in MOCK MODE");
  console.log("   Configure WHATSAPP_ACCESS_TOKEN in .env for real messaging");
}

// ============== API ENDPOINTS ==============

/**
 * Health Check
 */
app.get('/health', (req, res) => {
  res.json({
    status: mock_mode ? 'mock_mode' : 'healthy',
    phone_number_id: WHATSAPP_PHONE_NUMBER_ID || 'Not configured',
    mock_mode: mock_mode,
    timestamp: new Date().toISOString()
  });
});

/**
 * Send Text Message
 * POST /api/whatsapp/message
 * Body: { to, message }
 */
app.post('/api/whatsapp/message', async (req, res) => {
  try {
    const { to, message } = req.body;
    
    if (!to || !message) {
      return res.status(400).json({
        success: false,
        error: 'to and message are required'
      });
    }
    
    if (mock_mode) {
      // Mock response
      res.json({
        success: true,
        message_id: `mock_${Date.now()}`,
        status: 'sent',
        mock: true,
        message: 'Message sent (Mock Mode)'
      });
      return;
    }
    
    // Real WhatsApp API call
    const response = await axios.post(
      `https://graph.facebook.com/v17.0/${WHATSAPP_PHONE_NUMBER_ID}/messages`,
      {
        messaging_product: 'whatsapp',
        to: to,
        type: 'text',
        text: {
          body: message
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${WHATSAPP_ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    res.json({
      success: true,
      message_id: response.data.messages[0].id,
      status: 'sent'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.response?.data?.error?.message || error.message
    });
  }
});

/**
 * Send Template Message
 * POST /api/whatsapp/template
 * Body: { to, template_name, language, components }
 */
app.post('/api/whatsapp/template', async (req, res) => {
  try {
    const { to, template_name, language = 'en', components = [] } = req.body;
    
    if (!to || !template_name) {
      return res.status(400).json({
        success: false,
        error: 'to and template_name are required'
      });
    }
    
    if (mock_mode) {
      res.json({
        success: true,
        message_id: `mock_${Date.now()}`,
        status: 'sent',
        mock: true,
        message: 'Template sent (Mock Mode)'
      });
      return;
    }
    
    const response = await axios.post(
      `https://graph.facebook.com/v17.0/${WHATSAPP_PHONE_NUMBER_ID}/messages`,
      {
        messaging_product: 'whatsapp',
        to: to,
        type: 'template',
        template: {
          name: template_name,
          language: {
            code: language
          },
          components: components
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${WHATSAPP_ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    res.json({
      success: true,
      message_id: response.data.messages[0].id,
      status: 'sent'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.response?.data?.error?.message || error.message
    });
  }
});

/**
 * Send Media (Image/Document)
 * POST /api/whatsapp/media
 * Body: { to, media_url, caption, type }
 */
app.post('/api/whatsapp/media', async (req, res) => {
  try {
    const { to, media_url, caption, type = 'image' } = req.body;
    
    if (!to || !media_url) {
      return res.status(400).json({
        success: false,
        error: 'to and media_url are required'
      });
    }
    
    if (mock_mode) {
      res.json({
        success: true,
        message_id: `mock_${Date.now()}`,
        status: 'sent',
        mock: true,
        message: `Media sent (Mock Mode) - Type: ${type}`
      });
      return;
    }
    
    const response = await axios.post(
      `https://graph.facebook.com/v17.0/${WHATSAPP_PHONE_NUMBER_ID}/messages`,
      {
        messaging_product: 'whatsapp',
        to: to,
        type: type,
        [type]: {
          link: media_url,
          caption: caption || ''
        }
      },
      {
        headers: {
          'Authorization': `Bearer ${WHATSAPP_ACCESS_TOKEN}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    res.json({
      success: true,
      message_id: response.data.messages[0].id,
      status: 'sent'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.response?.data?.error?.message || error.message
    });
  }
});

/**
 * Get Contacts (from saved messages)
 * GET /api/whatsapp/contacts
 */
app.get('/api/whatsapp/contacts', (req, res) => {
  // In mock mode, return sample contacts
  const mock_contacts = [
    { phone: '+923161129505', name: 'Naz Sheikh', last_seen: '2026-03-28' },
    { phone: '+923001234567', name: 'Shama Naz', last_seen: '2026-03-27' },
    { phone: '+923119876543', name: 'Business Contact', last_seen: '2026-03-26' }
  ];
  
  res.json({
    success: true,
    contacts: mock_mode ? mock_contacts : [],
    mock: mock_mode
  });
});

/**
 * Get Message History (from logs)
 * GET /api/whatsapp/messages?limit=10
 */
app.get('/api/whatsapp/messages', (req, res) => {
  const limit = parseInt(req.query.limit) || 10;
  
  // Read from logs
  const log_file = path.join(__dirname, '..', 'logs', 'whatsapp_messages.json');
  
  let messages = [];
  if (fs.existsSync(log_file)) {
    const data = fs.readFileSync(log_file, 'utf-8');
    messages = JSON.parse(data).slice(0, limit);
  }
  
  res.json({
    success: true,
    messages: messages,
    count: messages.length
  });
});

/**
 * MCP Info
 */
app.get('/api/mcp/info', (req, res) => {
  res.json(mcp_info);
});

// ============== MESSAGE LOGGER ==============

function log_message(message_data) {
  """Log sent messages to file"""
  const log_file = path.join(__dirname, '..', 'logs', 'whatsapp_messages.json');
  
  let messages = [];
  if (fs.existsSync(log_file)) {
    const data = fs.readFileSync(log_file, 'utf-8');
    messages = JSON.parse(data);
  }
  
  messages.unshift({
    timestamp: new Date().toISOString(),
    ...message_data
  });
  
  // Keep last 100 messages
  messages = messages.slice(0, 100);
  
  fs.writeFileSync(log_file, JSON.stringify(messages, null, 2));
}

// ============== START SERVER ==============

if (require.main === module) {
  app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('   WHATSAPP MCP SERVER');
    console.log('='.repeat(60));
    console.log(`   Port: http://localhost:${PORT}`);
    console.log(`   Mode: ${mock_mode ? 'MOCK' : 'PRODUCTION'}`);
    console.log(`   Phone Number ID: ${WHATSAPP_PHONE_NUMBER_ID || 'Not configured'}`);
    console.log('='.repeat(60));
    console.log();
    console.log('   Endpoints:');
    console.log('   GET  /health - Health check');
    console.log('   POST /api/whatsapp/message - Send text message');
    console.log('   POST /api/whatsapp/template - Send template message');
    console.log('   POST /api/whatsapp/media - Send media (image/document)');
    console.log('   GET  /api/whatsapp/contacts - Get contacts');
    console.log('   GET  /api/whatsapp/messages - Get message history');
    console.log('   GET  /api/mcp/info - MCP info');
    console.log();
    console.log('='.repeat(60));
    
    // Open browser
    const open = require('open');
    open(`http://localhost:${PORT}/api/mcp/info`);
  });
}

module.exports = app;
