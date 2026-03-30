#!/usr/bin/env node
/**
 * MCP Email Server - Node.js Implementation
 * 
 * Exposes send_email tool via Model Context Protocol (MCP)
 * Sends emails via SMTP or Gmail API
 * 
 * Usage:
 *   node email_mcp.js
 * 
 * Configuration:
 *   ~/.config/qwen-code/email_config.json
 */

const fs = require('fs');
const path = require('path');
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');
const nodemailer = require('nodemailer');

// ============================================================================
// Configuration
// ============================================================================

const CONFIG_DIR = path.join(process.env.APPDATA || path.join(process.env.HOME, '.config'), 'qwen-code');
const CONFIG_FILE = path.join(CONFIG_DIR, 'email_config.json');

class EmailConfig {
  constructor() {
    this.smtp_server = process.env.SMTP_SERVER || 'smtp.gmail.com';
    this.smtp_port = parseInt(process.env.SMTP_PORT) || 587;
    this.email_address = process.env.EMAIL_ADDRESS || '';
    this.app_password = process.env.EMAIL_PASSWORD || '';
    
    // Load from config file if exists
    if (fs.existsSync(CONFIG_FILE)) {
      try {
        const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
        this.smtp_server = config.smtp_server || this.smtp_server;
        this.smtp_port = config.smtp_port || this.smtp_port;
        this.email_address = config.email || this.email_address;
        this.app_password = config.app_password || this.app_password;
      } catch (err) {
        console.error('Error loading config file:', err.message);
      }
    }
  }
  
  isConfigured() {
    return !!(this.email_address && this.app_password);
  }
  
  save() {
    // Ensure config directory exists
    if (!fs.existsSync(CONFIG_DIR)) {
      fs.mkdirSync(CONFIG_DIR, { recursive: true });
    }
    
    const config = {
      smtp_server: this.smtp_server,
      smtp_port: this.smtp_port,
      email: this.email_address,
      app_password: this.app_password
    };
    
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
    console.error(`Configuration saved to: ${CONFIG_FILE}`);
  }
}

// ============================================================================
// Email Sender
// ============================================================================

class EmailSender {
  constructor(config, logger) {
    this.config = config;
    this.logger = logger;
    this.transporter = null;
  }
  
  createTransporter() {
    if (!this.transporter) {
      this.transporter = nodemailer.createTransport({
        host: this.config.smtp_server,
        port: this.config.smtp_port,
        secure: false, // true for 465, false for other ports
        auth: {
          user: this.config.email_address,
          pass: this.config.app_password
        }
      });
    }
    return this.transporter;
  }
  
  async sendEmail(to, subject, body, html = false) {
    if (!this.config.isConfigured()) {
      return {
        success: false,
        error: 'Email not configured. Set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.'
      };
    }
    
    try {
      this.logger.info(`Sending email to: ${to}`);
      this.logger.info(`Subject: ${subject}`);
      
      const mailOptions = {
        from: this.config.email_address,
        to: to,
        subject: subject,
        text: html ? null : body,
        html: html ? body : null
      };
      
      const info = await this.createTransporter().sendMail(mailOptions);
      
      this.logger.info(`Email sent successfully: ${info.messageId}`);
      
      return {
        success: true,
        message: `Email sent to ${to}`,
        messageId: info.messageId,
        subject: subject,
        timestamp: new Date().toISOString()
      };
      
    } catch (error) {
      this.logger.error(`Error sending email: ${error.message}`);
      
      return {
        success: false,
        error: error.message
      };
    }
  }
}

// ============================================================================
// Logger
// ============================================================================

class Logger {
  constructor() {
    const logDir = path.join(process.cwd(), 'logs');
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
    this.logFile = path.join(logDir, 'mcp_email_server.log');
  }
  
  info(message) {
    const timestamp = new Date().toISOString();
    const logLine = `${timestamp} - INFO - ${message}\n`;
    this._write(logLine);
    console.error(logLine.trim());
  }
  
  error(message) {
    const timestamp = new Date().toISOString();
    const logLine = `${timestamp} - ERROR - ${message}\n`;
    this._write(logLine);
    console.error(logLine.trim());
  }
  
  debug(message) {
    const timestamp = new Date().toISOString();
    const logLine = `${timestamp} - DEBUG - ${message}\n`;
    this._write(logLine);
  }
  
  _write(message) {
    fs.appendFileSync(this.logFile, message);
  }
}

// ============================================================================
// MCP Server
// ============================================================================

class MCPEmailServer {
  constructor() {
    this.config = new EmailConfig();
    this.logger = new Logger();
    this.emailSender = new EmailSender(this.config, this.logger);
    
    this.server = new Server(
      {
        name: 'email-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );
    
    this.setupToolHandlers();
  }
  
  setupToolHandlers() {
    // List tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'send_email',
            description: 'Send an email via SMTP/Gmail. Requires recipient, subject, and body.',
            inputSchema: {
              type: 'object',
              properties: {
                to: {
                  type: 'string',
                  description: 'Recipient email address'
                },
                subject: {
                  type: 'string',
                  description: 'Email subject line'
                },
                body: {
                  type: 'string',
                  description: 'Email body content'
                },
                html: {
                  type: 'boolean',
                  description: 'Whether body is HTML format (default: false)',
                  default: false
                }
              },
              required: ['to', 'subject', 'body']
            }
          },
          {
            name: 'check_email_config',
            description: 'Check if email server is configured properly',
            inputSchema: {
              type: 'object',
              properties: {}
            }
          }
        ]
      };
    });
    
    // Call tool
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      this.logger.info(`Tool called: ${name}`);
      this.logger.info(`Arguments: ${JSON.stringify(args)}`);
      
      if (name === 'send_email') {
        return await this.handleSendEmail(args);
      } else if (name === 'check_email_config') {
        return await this.handleCheckConfig();
      } else {
        return {
          content: [{
            type: 'text',
            text: `Unknown tool: ${name}`
          }]
        };
      }
    });
  }
  
  async handleSendEmail(args) {
    const { to, subject, body, html = false } = args;
    
    if (!to) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ success: false, error: 'Missing "to" parameter' }, null, 2)
        }]
      };
    }
    
    if (!subject) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ success: false, error: 'Missing "subject" parameter' }, null, 2)
        }]
      };
    }
    
    if (!body) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ success: false, error: 'Missing "body" parameter' }, null, 2)
        }]
      };
    }
    
    const result = await this.emailSender.sendEmail(to, subject, body, html);
    
    return {
      content: [{
        type: 'text',
        text: JSON.stringify(result, null, 2)
      }]
    };
  }
  
  async handleCheckConfig() {
    const isConfigured = this.config.isConfigured();
    
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          configured: isConfigured,
          email: isConfigured ? this.config.email_address : 'Not configured',
          smtp_server: this.config.smtp_server,
          smtp_port: this.config.smtp_port
        }, null, 2)
      }]
    };
  }
  
  async run() {
    this.logger.info('Starting MCP Email Server (Node.js)...');
    this.logger.info(`Email configured: ${this.config.isConfigured()}`);
    this.logger.info(`Config file: ${CONFIG_FILE}`);
    
    console.error('\n' + '='.repeat(60));
    console.error('MCP Email Server (Node.js)');
    console.error('='.repeat(60));
    console.error(`Email: ${this.config.email_address || 'Not configured'}`);
    console.error(`SMTP: ${this.config.smtp_server}:${this.config.smtp_port}`);
    console.error(`Status: ${this.config.isConfigured() ? 'Configured' : 'Not configured'}`);
    console.error('='.repeat(60));
    console.error('\nStarting MCP server (stdio mode)...\n');
    
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
  }
}

// ============================================================================
// CLI
// ============================================================================

function showHelp() {
  console.log(`
MCP Email Server - Node.js Implementation

Usage:
  node email_mcp.js [options]

Options:
  --email EMAIL         Set email address
  --password PASSWORD   Set app password
  --smtp-server SERVER  Set SMTP server (default: smtp.gmail.com)
  --smtp-port PORT      Set SMTP port (default: 587)
  --save-config         Save configuration to config file
  --help                Show this help message

Configuration:
  Config file: ${CONFIG_FILE}
  
  Environment variables:
    EMAIL_ADDRESS     - Your email address
    EMAIL_PASSWORD    - Your app password
    SMTP_SERVER       - SMTP server (default: smtp.gmail.com)
    SMTP_PORT         - SMTP port (default: 587)

Examples:
  node email_mcp.js --email user@gmail.com --password abc123 --save-config
  node email_mcp.js
  EMAIL_ADDRESS=user@gmail.com EMAIL_PASSWORD=abc123 node email_mcp.js

For Gmail, use an App Password:
  https://support.google.com/accounts/answer/185833
`);
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    showHelp();
    process.exit(0);
  }
  
  const config = new EmailConfig();
  
  // Parse arguments
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--email':
        config.email_address = args[++i];
        break;
      case '--password':
        config.app_password = args[++i];
        break;
      case '--smtp-server':
        config.smtp_server = args[++i];
        break;
      case '--smtp-port':
        config.smtp_port = parseInt(args[++i]);
        break;
      case '--save-config':
        config.save();
        console.log('Configuration saved!');
        process.exit(0);
        break;
    }
  }
  
  // Check configuration
  if (!config.isConfigured()) {
    console.error('\n⚠️  WARNING: Email not configured!\n');
    console.error('Set up email credentials:\n');
    console.error('Option 1: Command line');
    console.error(`  node email_mcp.js --email your@email.com --password app-password --save-config\n`);
    console.error('Option 2: Environment variables');
    console.error('  set EMAIL_ADDRESS=your@email.com');
    console.error('  set EMAIL_PASSWORD=your-app-password\n');
    console.error('Option 3: Create config file');
    console.error(`  ${CONFIG_FILE}\n`);
    console.error('For Gmail, use an App Password:');
    console.error('  https://support.google.com/accounts/answer/185833\n');
  }
  
  // Run server
  const server = new MCPEmailServer();
  server.run().catch((err) => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}

main();
