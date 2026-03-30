"""
Gmail Watcher - Polling Module
Implements periodic checking of Gmail inbox every 5 minutes
"""
import time
import threading
import logging
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from gmail_auth import authenticate_gmail

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gmail_watcher.log')),
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

class GmailWatcher:
    def __init__(self):
        self.service = None
        self.running = False
        self.poll_interval = 300  # 5 minutes in seconds
        self.last_checked = None
    
    def start_polling(self):
        """Start the polling mechanism"""
        self.running = True
        logger.info(f"Starting Gmail watcher (checking every {self.poll_interval} seconds)")
        
        while self.running:
            try:
                self.check_new_emails()
                logger.info(f"Next check in {self.poll_interval} seconds")
                
                # Wait for the specified interval, but check if we should stop periodically
                for _ in range(self.poll_interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                self.stop_polling()
            except Exception as e:
                logger.error(f"Error during polling: {e}", exc_info=True)
                time.sleep(60)  # Wait a minute before retrying
    
    def stop_polling(self):
        """Stop the polling mechanism"""
        self.running = False
        logger.info("Gmail watcher stopped")
    
    def check_new_emails(self):
        """Check for new unread emails"""
        logger.info("Checking for new emails...")
        
        # Authenticate if needed
        if not self.service:
            try:
                self.service = authenticate_gmail()
                if not self.service:
                    logger.error("Failed to authenticate with Gmail")
                    return
            except Exception as e:
                logger.error(f"Authentication error: {e}", exc_info=True)
                return
        
        try:
            # Call the Gmail API to list messages
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['INBOX'],
                q='is:unread'
            ).execute()
            
            messages = results.get('messages', [])
            
            if messages:
                logger.info(f"Found {len(messages)} unread emails")
                # Process each unread email
                for message in messages:
                    self.process_email(message['id'])
            else:
                logger.info("No unread emails found")
                
            self.last_checked = datetime.now()
            
        except Exception as e:
            logger.error(f"Error checking emails: {e}", exc_info=True)
            # Reset service in case of authentication error
            self.service = None
    
    def process_email(self, msg_id):
        """Process a single email - extract sender, subject, snippet, timestamp"""
        try:
            # Get the message details
            message = self.service.users().messages().get(
                userId='me', 
                id=msg_id
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            
            # Initialize variables
            sender = 'Unknown Sender'
            subject = 'No Subject'
            timestamp = ''
            
            # Extract sender, subject, and timestamp from headers
            for header in headers:
                name = header['name'].lower()
                value = header['value']
                
                if name == 'from':
                    sender = value
                elif name == 'subject':
                    subject = value
                elif name == 'date':
                    timestamp = value
            
            # Extract snippet from the message body
            snippet = message.get('snippet', '')
            
            # Log extracted information
            logger.info(f"  From: {sender}")
            logger.info(f"  Subject: {subject}")
            logger.info(f"  Snippet: {snippet[:100]}...")  # First 100 chars of snippet
            logger.info(f"  Date: {timestamp}")
            
            # Create markdown file in Needs_Action folder
            self.create_markdown_file(sender, subject, snippet, timestamp, msg_id)
            
            # Mark as read after processing (optional)
            # self.mark_as_read(msg_id)
            
            return {
                'id': msg_id,
                'sender': sender,
                'subject': subject,
                'snippet': snippet,
                'timestamp': timestamp
            }
            
        except Exception as e:
            logger.error(f"Error processing email {msg_id}: {e}", exc_info=True)
            return None
    
    def create_markdown_file(self, sender, subject, snippet, timestamp, msg_id):
        """Create a markdown file in the Needs_Action folder"""
        import os
        from datetime import datetime
        
        # Sanitize the subject to create a valid filename
        sanitized_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not sanitized_subject:
            sanitized_subject = "untitled_email"
        
        # Create filename with timestamp to avoid duplicates
        timestamp_safe = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Gmail_{timestamp_safe}_{sanitized_subject[:50]}.md"
        
        # Define the path for the Needs_Action folder
        needs_action_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Needs_Action")
        
        # Create the full file path
        filepath = os.path.join(needs_action_path, filename)
        
        # Create the markdown content
        markdown_content = f"""# Email from {sender}

## Subject
{subject}

## Timestamp
{timestamp}

## Email ID
{msg_id}

## Snippet
{snippet}

## Action Required
- [ ] Review email content
- [ ] Determine appropriate response
- [ ] Take necessary action
- [ ] Close task when completed

---
*This file was automatically generated from an email received in your Gmail inbox.*
"""
        
        try:
            # Ensure the Needs_Action directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Write the markdown content to the file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"  Created markdown file: {filename}")
            
        except Exception as e:
            logger.error(f"  Error creating markdown file: {e}", exc_info=True)
    
    def mark_as_read(self, msg_id):
        """Mark an email as read to prevent reprocessing"""
        try:
            # Remove the UNREAD label
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            logger.debug(f"Marked email {msg_id} as read")
        except Exception as e:
            logger.error(f"Error marking email as read: {e}", exc_info=True)

def run_watcher():
    """Run the Gmail watcher"""
    logger.info("Initializing Gmail watcher...")
    watcher = GmailWatcher()
    
    try:
        watcher.start_polling()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        watcher.stop_polling()

if __name__ == '__main__':
    run_watcher()