#!/usr/bin/env python3
"""
Test script to simulate GitHub webhook events.
This script sends a simulated GitHub Sponsors webhook payload to your webhook server
to test the integration without needing to set up a real GitHub webhook.
"""

import os
import sys
import json
import hmac
import hashlib
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("WebhookTest")

def generate_signature(payload, secret):
    """Generate a GitHub webhook signature for the payload"""
    mac = hmac.new(
        secret.encode('utf-8'),
        msg=payload.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return f"sha256={mac.hexdigest()}"

def test_webhook():
    """Test the webhook server by sending a simulated GitHub Sponsors event"""
    # Load environment variables
    load_dotenv()
    
    # Get webhook secret
    webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET')
    
    if not webhook_secret:
        logger.error("GITHUB_WEBHOOK_SECRET not found in environment variables")
        sys.exit(1)
    
    # Get webhook URL from command line or use default
    if len(sys.argv) > 1:
        webhook_url = sys.argv[1]
    else:
        webhook_url = "http://localhost:5000/webhook/github"
    
    # Create a sample sponsorship event payload
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    payload = {
        "action": "created",
        "sponsorship": {
            "sponsor": {
                "login": "test-user",
                "name": "Test User"
            },
            "tier": {
                "name": "Test Tier",
                "monthly_price_in_dollars": 10
            },
            "created_at": current_time,
            "is_one_time_payment": False
        }
    }
    
    # Convert payload to JSON
    payload_json = json.dumps(payload)
    
    # Generate signature
    signature = generate_signature(payload_json, webhook_secret)
    
    # Set headers
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "sponsorship",
        "X-Hub-Signature-256": signature
    }
    
    # Send the request
    try:
        logger.info(f"Sending test webhook to {webhook_url}")
        response = requests.post(webhook_url, data=payload_json, headers=headers)
        
        # Check response
        if response.status_code == 200:
            logger.info("Webhook test successful!")
            print(f"\n✅ Success! Webhook server responded with status code {response.status_code}")
            print(f"Response: {response.text}")
        else:
            logger.error(f"Webhook test failed with status code {response.status_code}")
            print(f"\n❌ Error: Webhook server responded with status code {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        logger.error(f"Error sending webhook: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def print_usage():
    """Print usage information"""
    print(f"Usage: {sys.argv[0]} [webhook_url]")
    print("If webhook_url is not provided, http://localhost:5000/webhook/github will be used.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["-h", "--help"]:
        print_usage()
        sys.exit(0)
    
    print("Testing GitHub webhook integration...")
    test_webhook()