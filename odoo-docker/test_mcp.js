const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');

async function test() {
  console.log('Connecting to MCP server...');
  const transport = new StdioClientTransport({
    command: 'node',
    args: ['email_mcp.js']
  });
  
  const client = new Client(transport);
  await client.connect();
  console.log('Connected!');
  
  const tools = await client.listTools();
  console.log('Available tools:', JSON.stringify(tools.tools, null, 2));
  
  const configResult = await client.callTool({
    name: 'check_email_config',
    arguments: {}
  });
  console.log('Config check:', configResult.content[0].text);
  
  const emailResult = await client.callTool({
    name: 'send_email',
    arguments: {
      to: 'shama20302022@gmail.com',
      subject: 'Test from AI employee',
      body: 'This is a test email sent via MCP server.',
      html: false
    }
  });
  console.log('Email result:', emailResult.content[0].text);
  
  process.exit(0);
}

test().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
