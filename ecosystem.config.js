/**
 * PM2 Ecosystem Configuration
 * Gold Tier - All Services Management
 * 
 * Usage:
 *   pm2 start ecosystem.config.js
 *   pm2 start ecosystem.config.js --only facebook-watcher
 *   pm2 restart ecosystem.config.js --only facebook-watcher
 *   pm2 stop ecosystem.config.js
 *   pm2 delete ecosystem.config.js
 *   pm2 monit
 *   pm2 logs
 */

module.exports = {
  apps: [
    {
      name: 'facebook-watcher',
      script: 'watcher/facebook_instagram_watcher.py',
      interpreter: 'python',
      args: '--interval 60',
      cwd: 'C:\\Users\\AA\\Desktop\\gold_tier',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/pm2-facebook-watcher-error.log',
      out_file: './logs/pm2-facebook-watcher-out.log',
      log_file: './logs/pm2-facebook-watcher-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    
    {
      name: 'gmail-watcher',
      script: 'gmail_watcher.py',
      interpreter: 'python',
      args: '',
      cwd: 'C:\\Users\\AA\\Desktop\\gold_tier',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/pm2-gmail-watcher-error.log',
      out_file: './logs/pm2-gmail-watcher-out.log',
      log_file: './logs/pm2-gmail-watcher-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    
    {
      name: 'whatsapp-watcher',
      script: 'whatsapp_watcher.py',
      interpreter: 'python',
      args: '',
      cwd: 'C:\\Users\\AA\\Desktop\\gold_tier',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/pm2-whatsapp-watcher-error.log',
      out_file: './logs/pm2-whatsapp-watcher-out.log',
      log_file: './logs/pm2-whatsapp-watcher-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    
    {
      name: 'orchestrator',
      script: 'orchestrator.py',
      interpreter: 'python',
      args: '',
      cwd: 'C:\\Users\\AA\\Desktop\\gold_tier',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/pm2-orchestrator-error.log',
      out_file: './logs/pm2-orchestrator-out.log',
      log_file: './logs/pm2-orchestrator-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    
    {
      name: 'scheduler',
      script: 'scheduler.py',
      interpreter: 'python',
      args: '',
      cwd: 'C:\\Users\\AA\\Desktop\\gold_tier',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/pm2-scheduler-error.log',
      out_file: './logs/pm2-scheduler-out.log',
      log_file: './logs/pm2-scheduler-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    
    {
      name: 'auto-processor',
      script: 'auto_processor.py',
      interpreter: 'python',
      args: '',
      cwd: 'C:\\Users\\AA\\Desktop\\gold_tier',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/pm2-auto-processor-error.log',
      out_file: './logs/pm2-auto-processor-out.log',
      log_file: './logs/pm2-auto-processor-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    
    {
      name: 'mcp-email-server',
      script: 'mcp_email_server.py',
      interpreter: 'python',
      args: '',
      cwd: 'C:\\Users\\AA\\Desktop\\gold_tier',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/pm2-mcp-email-error.log',
      out_file: './logs/pm2-mcp-email-out.log',
      log_file: './logs/pm2-mcp-email-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    },
    
    {
      name: 'odoo-mcp-server',
      script: 'odoo_mcp_server.py',
      interpreter: 'python',
      args: '',
      cwd: 'C:\\Users\\AA\\Desktop\\gold_tier',
      env: {
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/pm2-odoo-mcp-error.log',
      out_file: './logs/pm2-odoo-mcp-out.log',
      log_file: './logs/pm2-odoo-mcp-combined.log',
      time: true,
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
