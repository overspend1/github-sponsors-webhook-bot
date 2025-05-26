#!/usr/bin/env python3
"""
Handles payment alerts from emails via IMAP.

This module will connect to an IMAP server to:
- Fetch new emails from a specified account.
- Parse emails to identify UPI and HDFC Bank payment notifications.
- Extract payment details (amount, sender/description, transaction ID, timestamp).
"""

import os
import logging
import imaplib
import email
from email.header import decode_header
from datetime import datetime

logger = logging.getLogger("GitHubSponsorsBot.ImapAlerts")

# Environment variables for IMAP (ensure these are set)
IMAP_HOST = os.getenv('IMAP_HOST')
IMAP_PORT = os.getenv('IMAP_PORT', 993) # Default to 993 for IMAP SSL
IMAP_USER = os.getenv('IMAP_USER')
IMAP_PASSWORD = os.getenv('IMAP_PASSWORD')
IMAP_MAILBOX = os.getenv('IMAP_MAILBOX', 'INBOX')
# Optional: Define specific sender emails or subjects to filter for UPI/HDFC
UPI_EMAIL_SENDER_FILTER = os.getenv('UPI_EMAIL_SENDER_FILTER')
HDFC_EMAIL_SENDER_FILTER = os.getenv('HDFC_EMAIL_SENDER_FILTER')

class ImapAlerts:
    def __init__(self, telegram_bot):
        self.telegram_bot = telegram_bot
        self.enabled = False
        if not all([IMAP_HOST, IMAP_USER, IMAP_PASSWORD]):
            logger.error("IMAP configuration (HOST, USER, PASSWORD) incomplete. IMAP alerts will be disabled.")
        else:
            self.enabled = True
            logger.info(f"IMAP Alerts initialized for user {IMAP_USER} on host {IMAP_HOST}")

    def _connect(self):
        """Connects to the IMAP server."""
        try:
            if str(IMAP_PORT) == '993': # Common port for IMAP SSL
                mail = imaplib.IMAP4_SSL(IMAP_HOST, int(IMAP_PORT))
            else:
                mail = imaplib.IMAP4(IMAP_HOST, int(IMAP_PORT))
            mail.login(IMAP_USER, IMAP_PASSWORD)
            mail.select(IMAP_MAILBOX)
            logger.info(f"Successfully connected to IMAP server and selected mailbox '{IMAP_MAILBOX}'.")
            return mail
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            return None

    def check_for_new_emails(self):
        """
        Checks for new emails, parses them, and sends alerts.
        """
        if not self.enabled:
            return

        logger.info("Checking for new emails via IMAP...")
        mail = self._connect()
        if not mail:
            return

        try:
            # Search for unseen emails. Add more criteria if needed (e.g., SENDER, SUBJECT)
            status, messages = mail.search(None, 'UNSEEN')
            if status != 'OK':
                logger.error("Failed to search for emails.")
                return

            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} unseen emails.")

            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status == 'OK':
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Decode email subject
                            subject, encoding = decode_header(msg["Subject"])[0]
                            if isinstance(subject, bytes):
                                subject = subject.decode(encoding if encoding else "utf-8")
                            
                            # Decode sender
                            from_ = msg.get("From")
                            logger.info(f"Processing email from: {from_}, subject: {subject}")

                            # Get email body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    content_disposition = str(part.get("Content-Disposition"))
                                    try:
                                        if content_type == "text/plain" and "attachment" not in content_disposition:
                                            body = part.get_payload(decode=True).decode()
                                            break
                                    except Exception as e:
                                        logger.warning(f"Could not decode part of email: {e}")
                            else:
                                try:
                                    body = msg.get_payload(decode=True).decode()
                                except Exception as e:
                                    logger.warning(f"Could not decode email body: {e}")
                            
                            # TODO: Implement parsing logic for UPI and HDFC notifications
                            # This will be complex and require specific rules based on email formats.
                            payment_details = self.parse_payment_email(subject, from_, body)

                            if payment_details:
                                alert_message = self.format_email_payment_message(payment_details)
                                self.telegram_bot.send_message(alert_message)
                                logger.info(f"Sent alert for payment: {payment_details.get('type')}")
                                # Optionally, mark email as read or move it
                                # mail.store(email_id, '+FLAGS', '\\Seen')
                            else:
                                logger.info(f"Email from {from_} with subject '{subject}' did not match payment patterns.")
                else:
                    logger.error(f"Failed to fetch email ID {email_id}")
        except Exception as e:
            logger.error(f"Error during email processing: {e}")
        finally:
            if mail:
                mail.close()
                mail.logout()
                logger.info("IMAP connection closed.")
        logger.info("Finished checking IMAP emails.")

    def parse_payment_email(self, subject, from_address, body):
        """
        Parses email content to extract payment details.
        This needs to be highly customized based on the exact format of UPI/HDFC emails.
        Returns a dictionary with extracted details or None.
        """
        # Placeholder - very basic example
        # You'll need robust regex or string searching here.
        
        # Example for HDFC Credit Card Transaction (highly hypothetical)
        if HDFC_EMAIL_SENDER_FILTER and HDFC_EMAIL_SENDER_FILTER.lower() in from_address.lower():
            if "transaction alert" in subject.lower() and "hdfc bank credit card" in body.lower():
                # Regex to find amount, merchant, etc.
                # amount_match = re.search(r"Rs\.([\d,]+\.\d{2})", body)
                # merchant_match = re.search(r"at ([\w\s]+) on", body)
                # if amount_match and merchant_match:
                #     return {
                #         "type": "HDFC Credit Card",
                #         "amount": amount_match.group(1),
                #         "currency": "INR",
                #         "description": merchant_match.group(1).strip(),
                #         "transaction_id": "N/A (extract if available)",
                #         "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Extract from email if possible
                #     }
                logger.info("Potential HDFC email found, parsing logic to be implemented.")
                pass # Added pass to fix indentation


        # Example for UPI Transaction (highly hypothetical)
        if UPI_EMAIL_SENDER_FILTER and UPI_EMAIL_SENDER_FILTER.lower() in from_address.lower():
            if "payment received" in subject.lower() and "upi" in body.lower():
                # Regex to find amount, sender, UPI ID etc.
                # amount_match = re.search(r"amount of INR ([\d,]+\.\d{2})", body)
                # sender_match = re.search(r"from ([\w\s@\.]+)", body) # Could be name or VPA
                # if amount_match and sender_match:
                #     return {
                #         "type": "UPI",
                #         "amount": amount_match.group(1),
                #         "currency": "INR",
                #         "description": f"Payment from {sender_match.group(1).strip()}",
                #         "transaction_id": "N/A (extract if available)",
                #         "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Extract from email if possible
                #     }
                logger.info("Potential UPI email found, parsing logic to be implemented.")
                pass # Added pass to fix indentation
        
        return None # No relevant payment found or parsing failed

    def format_email_payment_message(self, details):
        """
        Formats an alert message for a payment extracted from an email.
        """
        payment_type = details.get("type", "Unknown Payment")
        amount = details.get("amount", "N/A")
        currency = details.get("currency", "")
        description = details.get("description", "N/A")
        tx_id = details.get("transaction_id", "N/A")
        timestamp = details.get("timestamp", "N/A")

        message = (
            f"📧 *New {payment_type} Alert (from Email)*\n\n"
            f"*Amount:* {amount} {currency}\n"
            f"*Details:* {description}\n"
            f"*Transaction ID:* `{tx_id}`\n"
            f"*Timestamp:* {timestamp}\n"
        )
        return message

if __name__ == '__main__':
    # This section is for testing the module independently
    class MockTelegramBot:
        def send_message(self, message):
            print(f"MockTelegramBot sending: {message}")

    # Ensure environment variables are set for testing
    # from dotenv import load_dotenv
    # load_dotenv() # If you have a .env file for testing
    # IMAP_HOST = os.getenv('IMAP_HOST_TEST')
    # IMAP_USER = os.getenv('IMAP_USER_TEST')
    # IMAP_PASSWORD = os.getenv('IMAP_PASSWORD_TEST')

    if IMAP_HOST and IMAP_USER and IMAP_PASSWORD:
        logger.info("Running ImapAlerts standalone test...")
        mock_bot = MockTelegramBot()
        imap_alerter = ImapAlerts(mock_bot)
        if imap_alerter.enabled:
            imap_alerter.check_for_new_emails()
        else:
            logger.warning("IMAP alerts are disabled due to missing credentials.")
    else:
        logger.warning("Skipping ImapAlerts standalone test: IMAP credentials not found.")
