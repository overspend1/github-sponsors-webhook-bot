#!/usr/bin/env python3
"""
GitHub Sponsors and Multi-Source Payment Alert Bot

This bot:
- Receives GitHub Sponsors webhook events and sends notifications to Telegram.
- Polls Binance for new cryptocurrency deposits and P2P payments.
- Polls an IMAP email account for UPI and HDFC Bank payment notifications.
It provides real-time payment notifications with complete transaction details.

Usage:
    python github_sponsors_bot.py

Environment variables required:
    GITHUB_WEBHOOK_SECRET - Secret for verifying GitHub webhook signatures
    TELEGRAM_TOKEN - Telegram Bot API token
    TELEGRAM_CHAT_ID - Telegram chat ID to send notifications to
    WEBHOOK_HOST - Host to bind the webhook server to (default: 0.0.0.0)
    WEBHOOK_PORT - Port to bind the webhook server to (default: 5000)

    # Binance Alerts (Optional)
    BINANCE_API_KEY - Binance API Key
    BINANCE_API_SECRET - Binance API Secret
    BINANCE_POLL_INTERVAL - Interval in seconds to poll Binance (default: 300)

    # IMAP Email Alerts (Optional)
    IMAP_HOST - IMAP server host
    IMAP_PORT - IMAP server port (default: 993 for SSL)
    IMAP_USER - IMAP account username
    IMAP_PASSWORD - IMAP account password
    IMAP_MAILBOX - Mailbox to check (default: INBOX)
    IMAP_POLL_INTERVAL - Interval in seconds to poll IMAP server (default: 600)
    UPI_EMAIL_SENDER_FILTER - Optional: Email address or domain to filter UPI emails
    HDFC_EMAIL_SENDER_FILTER - Optional: Email address or domain to filter HDFC emails
"""

import os
import json
import logging
import hmac
import hashlib
import sys
import time
import threading
from datetime import datetime

import telegram
from telegram.ext import Updater, CommandHandler
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from payment_sources.binance_alerts import BinanceAlerts
from payment_sources.imap_alerts import ImapAlerts

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('github_sponsors_bot.log')
    ]
)
logger = logging.getLogger("GitHubSponsorsBot")

# Get configuration from environment variables
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', '0.0.0.0')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', 5000))
BINANCE_POLL_INTERVAL = int(os.getenv('BINANCE_POLL_INTERVAL', 300))
IMAP_POLL_INTERVAL = int(os.getenv('IMAP_POLL_INTERVAL', 600))

# Initialize Flask app
app = Flask(__name__)

# Global Alerter Instances
binance_alerter = None
imap_alerter = None

class TelegramBot:
    """Class to handle Telegram bot functionality"""
    
    def __init__(self, token, chat_id):
        """Initialize with Telegram Bot Token and Chat ID"""
        self.token = token
        self.chat_id = chat_id
        self.logger = logging.getLogger("GitHubSponsorsBot.Telegram")
        self.bot = telegram.Bot(token=token)
        
        # Initialize updater for handling commands
        self.updater = None
        self.initialized = False
    
    def initialize_bot(self):
        """Initialize the bot with command handlers"""
        try:
            self.updater = Updater(self.token, use_context=True)
            dispatcher = self.updater.dispatcher
            
            # Register command handlers
            dispatcher.add_handler(CommandHandler("start", self._start_command))
            dispatcher.add_handler(CommandHandler("help", self._help_command))
            dispatcher.add_handler(CommandHandler("status", self._status_command))
            
            # Log errors
            dispatcher.add_error_handler(self._error_handler)
            
            self.initialized = True
            self.logger.info("Telegram bot initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Telegram bot: {e}")
            return False
    
    def start_polling(self):
        """Start the bot polling for commands"""
        if not self.initialized:
            if not self.initialize_bot():
                return False
        
        try:
            self.updater.start_polling()
            self.logger.info("Telegram bot started polling")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start Telegram bot polling: {e}")
            return False
    
    def stop_polling(self):
        """Stop the bot polling"""
        if self.updater:
            self.updater.stop()
            self.logger.info("Telegram bot stopped polling")
    
    def send_message(self, message):
        """Send a message to the configured chat ID"""
        try:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=telegram.ParseMode.MARKDOWN
            )
            self.logger.info(f"Message sent to chat {self.chat_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False
    
    # Command handlers
    def _start_command(self, update, context):
        """Handle /start command"""
        update.message.reply_text(
            "GitHub Sponsors Webhook Bot started!\n\n"
            "This bot will notify you of GitHub Sponsors payments in real-time.\n\n"
            "Use /help to see available commands."
        )
    
    def _help_command(self, update, context):
        """Handle /help command"""
        help_text = (
            "*GitHub Sponsors Webhook Bot*\n\n"
            "This bot forwards GitHub Sponsors payment notifications directly to you.\n\n"
            "Available commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/status - Show current bot status"
        )
        update.message.reply_text(help_text, parse_mode=telegram.ParseMode.MARKDOWN)
    
    def _status_command(self, update, context):
        """Handle /status command"""
        status_text = (
            "*Bot Status*\n\n"
            "✅ Webhook server is running\n"
            "✅ Telegram notifications are enabled\n"
            "✅ GitHub webhook integration is active"
        )
        update.message.reply_text(status_text, parse_mode=telegram.ParseMode.MARKDOWN)
    
    def _error_handler(self, update, context):
        """Handle errors in the dispatcher"""
        self.logger.error(f"Update {update} caused error {context.error}")


# Initialize Telegram bot
telegram_bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)


def verify_github_signature(request_data, signature_header):
    """Verify that the webhook request is from GitHub using the webhook secret"""
    # GITHUB_WEBHOOK_SECRET is guaranteed to be present due to checks in main()
    if not signature_header:
        logger.error("No X-Hub-Signature-256 header in request")
        return False
    
    # The signature header starts with 'sha256='
    signature = signature_header.split('=')[1]
    
    # Create a new HMAC with the secret and request data
    mac = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode('utf-8'),
        msg=request_data,
        digestmod=hashlib.sha256
    )
    
    # Compare the computed signature with the one in the request
    return hmac.compare_digest(mac.hexdigest(), signature)


def format_sponsor_message(data):
    """Format the webhook data into a readable message"""
    try:
        # Extract the relevant information from the webhook payload
        action = data.get('action', 'unknown')
        
        # Different payload structure based on the event type
        if action == 'created' and 'sponsorship' in data:
            sponsorship = data['sponsorship']
            sponsor = sponsorship.get('sponsor', {})
            tier = sponsorship.get('tier', {})
            
            sponsor_name = sponsor.get('name') or sponsor.get('login', 'Unknown')
            sponsor_login = sponsor.get('login', 'Unknown')
            tier_name = tier.get('name', 'Unknown')
            amount = tier.get('monthly_price_in_dollars', 'Unknown')
            one_time = sponsorship.get('is_one_time_payment', False)
            created_at = sponsorship.get('created_at', datetime.now().isoformat())
            
            if isinstance(created_at, str):
                try:
                    created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    # If the date format is different, use it as is
                    pass
            
            payment_type = "one-time donation" if one_time else "monthly sponsorship"
            
            message = (
                f"🔔 *New GitHub Sponsor Payment Received*\n\n"
                f"*Sponsor:* {sponsor_name} (@{sponsor_login})\n"
                f"*Tier:* {tier_name}\n"
                f"*Amount:* ${amount}\n"
                f"*Type:* {payment_type}\n"
                f"*Timestamp:* {created_at}\n\n"
                f"*GitHub Profile:* https://github.com/{sponsor_login}"
            )
            
            return message
        
        # Handle other event types or return a generic message
        return f"GitHub Sponsors event received: {action}"
    
    except Exception as e:
        logger.error(f"Error formatting sponsor message: {e}")
        return "Error processing GitHub Sponsors webhook data"


@app.route('/webhook/github', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events"""
    # Get the signature from the request headers
    signature_header = request.headers.get('X-Hub-Signature-256')
    event_type = request.headers.get('X-GitHub-Event')
    
    # Get the raw request data for signature verification
    request_data = request.get_data()
    
    # Verify the signature
    if not verify_github_signature(request_data, signature_header):
        logger.error("Invalid signature in GitHub webhook request")
        return jsonify({"status": "error", "message": "Invalid signature"}), 401
    
    # Parse the JSON data
    data = request.json
    
    # Log the event
    logger.info(f"Received GitHub webhook event: {event_type}")
    
    # Process the event based on type
    if event_type == 'sponsorship':
        action = data.get('action')
        
        # We're primarily interested in new sponsorships
        if action == 'created':
            # Format the message
            message = format_sponsor_message(data)
            
            # Send the notification
            telegram_bot.send_message(message)
            
            # Log the notification
            logger.info(f"Sent notification for new sponsorship")
    
    # Return a success response
    return jsonify({"status": "success"}), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy"}), 200


def run_webhook_server():
    """Run the webhook server"""
    logger.info(f"Starting GitHub Sponsors webhook server on {WEBHOOK_HOST}:{WEBHOOK_PORT}")
    app.run(host=WEBHOOK_HOST, port=WEBHOOK_PORT)


# --- Polling functions for payment sources ---
def poll_binance_payments():
    """Periodically polls Binance for new payments."""
    global binance_alerter
    if not binance_alerter or not binance_alerter.enabled:
        logger.info("Binance alerter not initialized or disabled. Binance polling thread will not run.")
        return
    logger.info("Starting Binance payment polling thread.")
    while True:
        try:
            binance_alerter.check_for_new_payments()
        except Exception as e:
            logger.error(f"Error in Binance polling loop: {e}")
        time.sleep(BINANCE_POLL_INTERVAL)

def poll_imap_emails():
    """Periodically polls IMAP server for new payment emails."""
    global imap_alerter
    if not imap_alerter or not imap_alerter.enabled:
        logger.info("IMAP alerter not initialized or disabled. IMAP polling thread will not run.")
        return
    logger.info("Starting IMAP email polling thread.")
    while True:
        try:
            imap_alerter.check_for_new_emails()
        except Exception as e:
            logger.error(f"Error in IMAP polling loop: {e}")
        time.sleep(IMAP_POLL_INTERVAL)

def main():
    """Main function to run the bot"""
    global binance_alerter, imap_alerter

    # Validate required configuration
    if not GITHUB_WEBHOOK_SECRET:
        logger.error("GITHUB_WEBHOOK_SECRET not configured")
        print("Error: GITHUB_WEBHOOK_SECRET environment variable is required")
        sys.exit(1)
    
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not configured")
        print("Error: TELEGRAM_TOKEN environment variable is required")
        sys.exit(1)
    
    if not TELEGRAM_CHAT_ID:
        logger.error("TELEGRAM_CHAT_ID not configured")
        print("Error: TELEGRAM_CHAT_ID environment variable is required")
        sys.exit(1)
    
    # Initialize and start the Telegram bot
    if not telegram_bot.initialize_bot():
        logger.error("Failed to initialize Telegram bot")
        sys.exit(1)
    
    telegram_bot.start_polling()

    # Initialize payment alerters
    binance_alerter = BinanceAlerts(telegram_bot)
    imap_alerter = ImapAlerts(telegram_bot)

    # Start polling threads
    if binance_alerter.enabled:
        binance_thread = threading.Thread(target=poll_binance_payments, daemon=True)
        binance_thread.start()
    
    if imap_alerter.enabled:
        imap_thread = threading.Thread(target=poll_imap_emails, daemon=True)
        imap_thread.start()
    
    # Send startup message
    startup_message = (
        "🚀 *Multi-Source Payment Alert Bot Started*\n\n"
        "Listening for GitHub Sponsors webhooks.\n"
    )
    if binance_alerter and binance_alerter.enabled:
        startup_message += "Polling Binance for payments.\n"
    if imap_alerter and imap_alerter.enabled:
        startup_message += "Polling IMAP for email notifications.\n"
    
    telegram_bot.send_message(startup_message)
    
    try:
        # Run the webhook server (this will block until the server is stopped)
        run_webhook_server()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    except Exception as e:
        logger.error(f"Error running webhook server: {e}")
    finally:
        # Stop the Telegram bot
        telegram_bot.stop_polling()
        logger.info("Bot stopped")


if __name__ == "__main__":
    main()
