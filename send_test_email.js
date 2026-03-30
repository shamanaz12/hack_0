const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
  host: 'smtp.gmail.com',
  port: 587,
  secure: false,
  auth: {
    user: 'shama20302022@gmail.com',
    pass: 'nice786$$'
  }
});

transporter.sendMail({
  from: 'shama20302022@gmail.com',
  to: 'shama20302022@gmail.com',
  subject: 'Test from AI employee',
  text: 'This is a test email sent from the MCP email server.'
}, (err, info) => {
  if (err) {
    console.error('Error:', err.message);
    process.exit(1);
  } else {
    console.log('✓ Email sent successfully!');
    console.log('Message ID:', info.messageId);
    process.exit(0);
  }
});
