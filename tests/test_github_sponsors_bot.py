#!/usr/bin/env python3
"""
Unit tests for GitHub Sponsors Webhook Bot.
"""

import json
import hmac
import hashlib
import unittest
from unittest.mock import patch, MagicMock

import pytest
from flask import Flask

# Import the main module
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import github_sponsors_bot


class TestWebhookVerification(unittest.TestCase):
    """Test webhook signature verification functionality."""

    def setUp(self):
        """Set up test environment."""
        self.secret = "test_webhook_secret"
        self.payload = json.dumps({"action": "created", "sponsorship": {"sponsor": {"login": "test-user"}}})
        self.signature = hmac.new(
            self.secret.encode('utf-8'),
            msg=self.payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        self.header = f"sha256={self.signature}"

    def test_valid_signature(self):
        """Test that a valid signature is verified correctly."""
        with patch.object(github_sponsors_bot, 'GITHUB_WEBHOOK_SECRET', self.secret):
            result = github_sponsors_bot.verify_github_signature(
                self.payload.encode('utf-8'),
                self.header
            )
            self.assertTrue(result)

    def test_invalid_signature(self):
        """Test that an invalid signature is rejected."""
        with patch.object(github_sponsors_bot, 'GITHUB_WEBHOOK_SECRET', self.secret):
            invalid_header = f"sha256=invalid{self.signature[7:]}"
            result = github_sponsors_bot.verify_github_signature(
                self.payload.encode('utf-8'),
                invalid_header
            )
            self.assertFalse(result)

    def test_missing_signature(self):
        """Test handling of missing signature header."""
        with patch.object(github_sponsors_bot, 'GITHUB_WEBHOOK_SECRET', self.secret):
            result = github_sponsors_bot.verify_github_signature(
                self.payload.encode('utf-8'),
                None
            )
            self.assertFalse(result)


class TestMessageFormatting(unittest.TestCase):
    """Test message formatting functionality."""

    def test_format_sponsor_message(self):
        """Test formatting of sponsor messages."""
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
                "created_at": "2025-01-01T12:00:00Z",
                "is_one_time_payment": False
            }
        }

        message = github_sponsors_bot.format_sponsor_message(payload)
        
        # Check that the message contains the expected information
        self.assertIn("Test User", message)
        self.assertIn("@test-user", message)
        self.assertIn("Test Tier", message)
        self.assertIn("$10", message)
        self.assertIn("monthly sponsorship", message)
        self.assertIn("2025-01-01", message)


class TestWebhookEndpoint(unittest.TestCase):
    """Test the webhook endpoint."""

    def setUp(self):
        """Set up test environment."""
        self.app = github_sponsors_bot.app.test_client()
        self.secret = "test_webhook_secret"
        self.payload = {
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
                "created_at": "2025-01-01T12:00:00Z",
                "is_one_time_payment": False
            }
        }
        self.payload_json = json.dumps(self.payload)
        self.signature = hmac.new(
            self.secret.encode('utf-8'),
            msg=self.payload_json.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        self.headers = {
            'X-Hub-Signature-256': f"sha256={self.signature}",
            'X-GitHub-Event': 'sponsorship',
            'Content-Type': 'application/json'
        }

    @patch('github_sponsors_bot.verify_github_signature')
    @patch('github_sponsors_bot.telegram_bot')
    def test_valid_webhook_request(self, mock_telegram_bot, mock_verify):
        """Test handling of a valid webhook request."""
        mock_verify.return_value = True
        mock_telegram_bot.send_message = MagicMock(return_value=True)

        with patch.object(github_sponsors_bot, 'GITHUB_WEBHOOK_SECRET', self.secret):
            response = self.app.post(
                '/webhook/github',
                data=self.payload_json,
                headers=self.headers
            )
            
            # Check response
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['status'], 'success')
            
            # Check that the message was sent
            mock_telegram_bot.send_message.assert_called_once()

    @patch('github_sponsors_bot.verify_github_signature')
    @patch('github_sponsors_bot.telegram_bot')
    def test_invalid_signature(self, mock_telegram_bot, mock_verify):
        """Test handling of a request with invalid signature."""
        mock_verify.return_value = False
        
        response = self.app.post(
            '/webhook/github',
            data=self.payload_json,
            headers=self.headers
        )
        
        # Check response
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Invalid signature')
        
        # Check that no message was sent
        mock_telegram_bot.send_message.assert_not_called()


if __name__ == '__main__':
    unittest.main()