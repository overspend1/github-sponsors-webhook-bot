#!/usr/bin/env python3
import os
import json
import logging
import hmac
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from telegram_api import TelegramAPI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('webhook_server.log')
    ]
)
logger = logging.getLogger("GitHubSponsorsWebhook")

# Initialize Flask app
app = Flask(__name__)

# Get configuration from environment variables
GITHUB_WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Initialize Telegram API
telegram = TelegramAPI(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, None)

def verify_github_signature(request_data, signature_header):
    """Verify that the webhook request is from GitHub using the webhook secret"""
    if not GITHUB_WEBHOOK_SECRET:
        logger.warning("GITHUB_WEBHOOK_SECRET not configured, skipping signature verification")
        return True
    
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
            telegram.send_message(message)
            
            # Log the notification
            logger.info(f"Sent notification for new sponsorship")
    
    # Return a success response
    return jsonify({"status": "success"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy"}), 200

def run_webhook_server(host='0.0.0.0', port=5000):
    """Run the webhook server"""
    logger.info(f"Starting GitHub Sponsors webhook server on {host}:{port}")
    app.run(host=host, port=port)

if __name__ == "__main__":
    # Get host and port from environment variables or use defaults
    host = os.getenv('WEBHOOK_HOST', '0.0.0.0')
    port = int(os.getenv('WEBHOOK_PORT', 5000))
    
    # Run the webhook server
    run_webhook_server(host, port)