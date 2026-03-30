/**
 * Qwen MCP Server - Social Media Opener
 * Opens Facebook & Instagram with SAVED SESSION
 * NO PASSWORD NEEDED - Uses browser's saved login
 * 
 * Features:
 * ✅ Opens Facebook Business Page
 * ✅ Opens Instagram Profile
 * ✅ Uses saved browser session
 * ✅ No login required if already logged in
 * 
 * Usage:
 *   node qwen_social_opener.js
 */

const { exec } = require('child_process');
const path = require('path');
const dotenv = require('dotenv');

// Load environment
dotenv.config();

// Configuration
const FACEBOOK_PROFILE_ID = process.env.FACEBOOK_PAGE_ID || '61578524116357';
const INSTAGRAM_USERNAME = process.env.INSTAGRAM_USERNAME || 'shamaansari5576';

// URLs
const FACEBOOK_BUSINESS_URL = 'https://business.facebook.com';
const FACEBOOK_PROFILE_URL = `https://www.facebook.com/profile.php?id=${FACEBOOK_PROFILE_ID}`;
const INSTAGRAM_URL = `https://www.instagram.com/${INSTAGRAM_USERNAME}/`;
const META_BUSINESS_URL = 'https://business.facebook.com/overview';

console.log('='.repeat(60));
console.log('   QWEN MCP - SOCIAL MEDIA OPENER');
console.log('   Saved Session - No Password Needed!');
console.log('='.repeat(60));
console.log();
console.log(`Facebook Profile: ${FACEBOOK_PROFILE_ID}`);
console.log(`Instagram: @${INSTAGRAM_USERNAME}`);
console.log();
console.log('Opening platforms...');
console.log();

// Open Facebook Business
console.log('1. Opening Facebook Business...');
exec(`start ${FACEBOOK_BUSINESS_URL}`, (err) => {
  if (err) console.error('Error opening Facebook Business:', err);
});

// Wait 2 seconds
setTimeout(() => {
  // Open Facebook Profile
  console.log('2. Opening Facebook Profile...');
  exec(`start ${FACEBOOK_PROFILE_URL}`, (err) => {
    if (err) console.error('Error opening Facebook Profile:', err);
  });
}, 2000);

// Wait 4 seconds
setTimeout(() => {
  // Open Instagram
  console.log('3. Opening Instagram...');
  exec(`start ${INSTAGRAM_URL}`, (err) => {
    if (err) console.error('Error opening Instagram:', err);
  });
}, 4000);

// Wait 6 seconds
setTimeout(() => {
  // Open Meta Business Suite
  console.log('4. Opening Meta Business Suite...');
  exec(`start ${META_BUSINESS_URL}`, (err) => {
    if (err) console.error('Error opening Meta Business:', err);
  });
}, 6000);

// Final message
setTimeout(() => {
  console.log();
  console.log('='.repeat(60));
  console.log('   ✅ ALL PLATFORMS OPENED!');
  console.log('='.repeat(60));
  console.log();
  console.log('NOTE: If your browser saved your login:');
  console.log('  - You will be automatically logged in');
  console.log('  - No password needed!');
  console.log();
  console.log('If not logged in:');
  console.log('  1. Login once in your browser');
  console.log('  2. Check "Remember me" or "Keep me logged in"');
  console.log('  3. Next time this script runs, auto-login!');
  console.log();
  console.log('='.repeat(60));
}, 8000);
