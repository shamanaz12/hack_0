/**
 * Google Calendar MCP Server
 * Gold Tier - Calendar Management
 * 
 * Features:
 * - Create events
 * - Update events
 * - Delete events
 * - List events
 * - Get event details
 * 
 * Usage:
 *   node calendar_mcp.js
 *   node calendar_mcp.js --test
 */

const express = require('express');
const axios = require('axios');
const { google } = require('googleapis');
const dotenv = require('dotenv');
const path = require('path');
const fs = require('fs');

// Load environment
dotenv.config();

// Configuration
const PORT = process.env.CALENDAR_PORT || 3002;
const GOOGLE_CALENDAR_ID = process.env.GOOGLE_CALENDAR_ID || 'primary';
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID || '';
const GOOGLE_CLIENT_SECRET = process.env.GOOGLE_CLIENT_SECRET || '';
const GOOGLE_REFRESH_TOKEN = process.env.GOOGLE_REFRESH_TOKEN || '';

// Initialize OAuth2
const oauth2Client = new google.auth.OAuth2(
  GOOGLE_CLIENT_ID,
  GOOGLE_CLIENT_SECRET,
  'https://developers.google.com/oauthplayground'
);

if (GOOGLE_REFRESH_TOKEN) {
  oauth2Client.setCredentials({
    refresh_token: GOOGLE_REFRESH_TOKEN
  });
}

const calendar = google.calendar({ version: 'v3', auth: oauth2Client });

// Express app
const app = express();
app.use(express.json());

// MCP Server info
const mcp_info = {
  name: 'Google Calendar MCP',
  version: '1.0.0',
  description: 'Gold Tier Calendar Management',
  features: [
    'create_event',
    'update_event',
    'delete_event',
    'list_events',
    'get_event'
  ]
};

// ============== API ENDPOINTS ==============

/**
 * Health Check
 */
app.get('/health', async (req, res) => {
  try {
    await calendar.calendars.get({ calendarId: GOOGLE_CALENDAR_ID });
    res.json({
      status: 'healthy',
      calendar: GOOGLE_CALENDAR_ID,
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
 * Create Event
 * POST /api/calendar/events
 * Body: { title, description, startTime, endTime, location, attendees }
 */
app.post('/api/calendar/events', async (req, res) => {
  try {
    const { title, description, startTime, endTime, location, attendees } = req.body;
    
    if (!title || !startTime || !endTime) {
      return res.status(400).json({
        success: false,
        error: 'Title, startTime, and endTime are required'
      });
    }
    
    const event = {
      summary: title,
      description: description || '',
      location: location || '',
      start: {
        dateTime: new Date(startTime).toISOString(),
        timeZone: 'Asia/Karachi'
      },
      end: {
        dateTime: new Date(endTime).toISOString(),
        timeZone: 'Asia/Karachi'
      },
      attendees: attendees ? attendees.map(email => ({ email })) : []
    };
    
    const response = await calendar.events.insert({
      calendarId: GOOGLE_CALENDAR_ID,
      resource: event,
      sendUpdates: attendees && attendees.length > 0 ? 'all' : 'none'
    });
    
    res.json({
      success: true,
      event_id: response.data.id,
      htmlLink: response.data.htmlLink,
      message: 'Event created successfully'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Update Event
 * PUT /api/calendar/events/:eventId
 * Body: { title, description, startTime, endTime, location }
 */
app.put('/api/calendar/events/:eventId', async (req, res) => {
  try {
    const { eventId } = req.params;
    const { title, description, startTime, endTime, location } = req.body;
    
    // Get existing event
    const existingEvent = await calendar.events.get({
      calendarId: GOOGLE_CALENDAR_ID,
      eventId: eventId
    });
    
    const updatedEvent = {
      ...existingEvent.data,
      summary: title || existingEvent.data.summary,
      description: description || existingEvent.data.description,
      location: location || existingEvent.data.location
    };
    
    if (startTime) {
      updatedEvent.start = {
        dateTime: new Date(startTime).toISOString(),
        timeZone: 'Asia/Karachi'
      };
    }
    
    if (endTime) {
      updatedEvent.end = {
        dateTime: new Date(endTime).toISOString(),
        timeZone: 'Asia/Karachi'
      };
    }
    
    const response = await calendar.events.update({
      calendarId: GOOGLE_CALENDAR_ID,
      eventId: eventId,
      resource: updatedEvent,
      sendUpdates: 'all'
    });
    
    res.json({
      success: true,
      event_id: response.data.id,
      htmlLink: response.data.htmlLink,
      message: 'Event updated successfully'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Delete Event
 * DELETE /api/calendar/events/:eventId
 */
app.delete('/api/calendar/events/:eventId', async (req, res) => {
  try {
    const { eventId } = req.params;
    
    await calendar.events.delete({
      calendarId: GOOGLE_CALENDAR_ID,
      eventId: eventId
    });
    
    res.json({
      success: true,
      message: 'Event deleted successfully'
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * List Events
 * GET /api/calendar/events?maxResults=10&timeMin=2026-03-28
 */
app.get('/api/calendar/events', async (req, res) => {
  try {
    const { maxResults = 10, timeMin, timeMax } = req.query;
    
    const params = {
      calendarId: GOOGLE_CALENDAR_ID,
      maxResults: parseInt(maxResults),
      singleEvents: true,
      orderBy: 'startTime'
    };
    
    if (timeMin) params.timeMin = new Date(timeMin).toISOString();
    if (timeMax) params.timeMax = new Date(timeMax).toISOString();
    
    const response = await calendar.events.list(params);
    
    res.json({
      success: true,
      events: response.data.items.map(event => ({
        id: event.id,
        title: event.summary,
        description: event.description,
        startTime: event.start.dateTime || event.start.date,
        endTime: event.end.dateTime || event.end.date,
        location: event.location,
        htmlLink: event.htmlLink
      })),
      count: response.data.items.length
    });
    
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

/**
 * Get Event
 * GET /api/calendar/events/:eventId
 */
app.get('/api/calendar/events/:eventId', async (req, res) => {
  try {
    const { eventId } = req.params;
    
    const event = await calendar.events.get({
      calendarId: GOOGLE_CALENDAR_ID,
      eventId: eventId
    });
    
    res.json({
      success: true,
      event: {
        id: event.data.id,
        title: event.data.summary,
        description: event.data.description,
        startTime: event.data.start.dateTime || event.data.start.date,
        endTime: event.data.end.dateTime || event.data.end.date,
        location: event.data.location,
        attendees: event.data.attendees || [],
        htmlLink: event.data.htmlLink
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
    console.log('   GOOGLE CALENDAR MCP SERVER');
    console.log('='.repeat(60));
    console.log(`   Port: http://localhost:${PORT}`);
    console.log(`   Calendar: ${GOOGLE_CALENDAR_ID}`);
    console.log('='.repeat(60));
    console.log();
    console.log('   Endpoints:');
    console.log('   GET  /health - Health check');
    console.log('   GET  /api/calendar/events - List events');
    console.log('   POST /api/calendar/events - Create event');
    console.log('   PUT  /api/calendar/events/:id - Update event');
    console.log('   DELETE /api/calendar/events/:id - Delete event');
    console.log('   GET  /api/calendar/events/:id - Get event');
    console.log('   GET  /api/mcp/info - MCP info');
    console.log();
    console.log('='.repeat(60));
    
    // Open browser
    const open = require('open');
    open(`http://localhost:${PORT}/api/mcp/info`);
  });
}

module.exports = app;
