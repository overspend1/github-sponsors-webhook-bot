# Multi-Source Payment Alert Bot Architecture

This document provides an overview of the Multi-Source Payment Alert Bot architecture, explaining the design decisions, component interactions, and data flow.

## System Overview

The Multi-Source Payment Alert Bot is designed to:

1.  **Receive GitHub Sponsors Webhook Events**:
    *   Process webhook events from GitHub when a new sponsorship is created.
    *   Verify the authenticity of these webhook events.
    *   Extract relevant information from the webhook payload.
2.  **Poll Binance for Payments**:
    *   Connect to the Binance API periodically.
    *   Fetch new cryptocurrency deposit information.
    *   Fetch completed P2P payment receipts.
3.  **Poll IMAP Server for Email Payments**:
    *   Connect to a configured IMAP email server periodically.
    *   Fetch new, unread emails.
    *   Parse emails to identify and extract details from UPI and HDFC Bank payment notifications.
4.  **Send Notifications**:
    *   Format and send notifications for all payment types to a configured Telegram chat.

The system is built as a single Python application that combines a webhook server (for GitHub), polling mechanisms for Binance and IMAP, and Telegram bot functionality.

## Component Architecture

```
                                External Systems
                                      │
                                      ▼
        ┌─────────────────────┐   ┌───────────────────┐   ┌───────────────────────────┐
        │ GitHub Webhooks     │   │ Binance API       │   │ IMAP Email Server         │
        │ (Sponsors Events)   │   │ (Deposits, P2P)   │   │ (UPI/HDFC Notifications)  │
        └──────────┬──────────┘   └─────────┬─────────┘   └────────────┬────────────┘
                   │                        │                          │
                   │ (HTTPS POST)           │ (API Calls)              │ (IMAP Commands)
                   ▼                        ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                                Multi-Source Payment Alert Bot                           │
│                                  (github_sponsors_bot.py)                               │
│                                                                                         │
├─────────────────────────┬──────────────────────────┬────────────────────────────────────┤
│                         │                          │                                    │
│  Flask Web Server       │  Payment Source Modules  │  Telegram Bot                      │
│  (Webhook Endpoint)     │  (Polling & Parsing)     │  (Notification & Commands)         │
│                         │                          │                                    │
└───────────┬─────────────┴─────────────┬────────────┴───────────────────┬────────────────┘
            │                           │                                │
            │ (Webhook Data)            │ (Payment Data)                 │ (Formatted Messages)
            ▼                           ▼                                ▼
┌─────────────────────────┐ ┌──────────────────────────┐   ┌───────────────────────────────────┐
│ Webhook Handler         │ │ BinanceAlerts Module     │   │ Telegram API                      │
│ - Signature Verification│ │ - API Client             │   │ (python-telegram-bot)             │
│ - GitHub Event Parsing  │ │ - Deposit/P2P Fetching   │   └───────────────────┬───────────────┘
│ - Message Formatting    │ │ - Message Formatting     │                       │
└─────────────────────────┘ └──────────────────────────┘                       │
                            ┌──────────────────────────┐                       │
                            │ ImapAlerts Module        │                       │
                            │ - IMAP Client            │                       │
                            │ - Email Fetching/Parsing │                       │
                            │ - Message Formatting     │                       │
                            └──────────────────────────┘                       │
                                                                               │
                                                                               ▼
                                                                     ┌─────────────────┐
                                                                     │ Telegram Chat   │
                                                                     │ (User/Group)    │
                                                                     └─────────────────┘
```

### Core Components

1.  **Main Application (`github_sponsors_bot.py`)**:
    *   **Flask Web Server**:
        *   Provides HTTP endpoints (e.g., `/webhook/github`) for receiving GitHub Sponsors webhook events.
        *   Handles routing and request/response processing.
        *   Exposes a health check endpoint (`/health`).
    *   **TelegramBot Class**:
        *   Manages all communication with the Telegram API using `python-telegram-bot`.
        *   Sends formatted notifications to the configured chat.
        *   Handles Telegram commands (e.g., `/start`, `/help`, `/status`).
        *   Manages bot lifecycle (initialization, polling for commands, shutdown).
    *   **Polling Orchestration**:
        *   Initializes and manages separate threads for polling Binance and IMAP payment sources at configured intervals.
    *   **Configuration Management**:
        *   Loads all necessary credentials and settings from environment variables using `python-dotenv`.

2.  **Payment Source Modules (`payment_sources/`)**:
    *   **`BinanceAlerts` Module (`binance_alerts.py`)**:
        *   Responsible for interacting with the Binance API.
        *   Fetches new cryptocurrency deposit data.
        *   Fetches completed P2P payment receipts.
        *   Formats Binance-specific payment data into notification messages.
        *   Manages Binance API credentials securely.
        *   Includes logic to avoid sending duplicate alerts (placeholder).
    *   **`ImapAlerts` Module (`imap_alerts.py`)**:
        *   Connects to a specified IMAP email server.
        *   Fetches new/unread emails from the configured mailbox.
        *   Parses email content (subject, sender, body) to identify and extract details from UPI and HDFC Bank payment notifications. This logic is highly dependent on email formats and may require custom regex/string parsing.
        *   Formats extracted email payment data into notification messages.
        *   Manages IMAP credentials securely.

## Data Flow

1.  **GitHub Sponsors Webhook**:
    *   GitHub sends a POST request to `/webhook/github`.
    *   The Flask server routes it to the `github_webhook` handler.
    *   **Signature Verification**: The handler verifies the `X-Hub-Signature-256` using the `GITHUB_WEBHOOK_SECRET`. Invalid requests are rejected.
    *   **Event Processing**: For valid 'sponsorship' events (action: 'created'), the payload is parsed by `format_sponsor_message`.
    *   **Notification**: The formatted message is sent via the `TelegramBot` instance.

2.  **Binance Payment Polling**:
    *   A dedicated thread periodically calls `binance_alerter.check_for_new_payments()`.
    *   The `BinanceAlerts` module connects to the Binance API using `BINANCE_API_KEY` and `BINANCE_API_SECRET`.
    *   It fetches deposit history and P2P trade history.
    *   New/relevant transactions are identified (logic to prevent duplicates is needed).
    *   Data is formatted by `format_deposit_message` or `format_p2p_message`.
    *   **Notification**: The formatted message is sent via the `TelegramBot` instance.

3.  **IMAP Email Polling (UPI/HDFC)**:
    *   A dedicated thread periodically calls `imap_alerter.check_for_new_emails()`.
    *   The `ImapAlerts` module connects to the IMAP server using `IMAP_HOST`, `IMAP_USER`, `IMAP_PASSWORD`, etc.
    *   It fetches new/unread emails from `IMAP_MAILBOX`.
    *   Emails are filtered (optionally by sender/subject) and parsed by `parse_payment_email` to extract UPI/HDFC transaction details.
    *   Extracted data is formatted by `format_email_payment_message`.
    *   **Notification**: The formatted message is sent via the `TelegramBot` instance.

## Security Considerations

1.  **Webhook Signature Verification**: Ensures GitHub webhook authenticity.
2.  **Environment Variables**: All sensitive data (API keys, tokens, passwords, secrets) are stored in environment variables and loaded via `.env` (which is gitignored).
3.  **Binance API Security**:
    *   API keys should be configured with minimal necessary permissions (e.g., read-only for transactions).
    *   Avoid enabling trading or withdrawal permissions unless essential.
4.  **IMAP Security**:
    *   Uses IMAP SSL/TLS by default (port 993).
    *   IMAP credentials should be for a dedicated or restricted-access email account if possible.
5.  **Docker Security**: If used, the application should run as a non-root user, expose only necessary ports, and pin dependencies.

## Performance Considerations

1.  **Webhook Processing**: Designed to be lightweight and respond quickly.
2.  **Polling Intervals**: `BINANCE_POLL_INTERVAL` and `IMAP_POLL_INTERVAL` should be set to reasonable values to balance responsiveness with API/server load.
3.  **Email Parsing**: Complex regex or inefficient string operations in `imap_alerts.py` could become a bottleneck if email volume is high or emails are very large. Optimize parsing logic.
4.  **Error Handling**: Robust error handling within polling loops and API interactions prevents crashes.
5.  **Threading**: Background tasks (polling) are handled in separate threads to prevent blocking the main application (Flask server and Telegram command polling).

## Configuration

The application is configured through environment variables, detailed in `.env.example` and the main `README.md`. This includes credentials for GitHub, Telegram, Binance, and IMAP, as well as polling intervals and server settings.

## Testing Strategy

1.  **Unit Testing**: Individual modules and functions (e.g., message formatters, parsing logic) should be tested in isolation, mocking external API/IMAP calls.
2.  **Integration Testing**:
    *   GitHub Webhook: `test_webhook.py` script.
    *   Binance/IMAP: Standalone test blocks within `binance_alerts.py` and `imap_alerts.py` can be used with test credentials or mocked responses.
3.  **Manual Testing**: End-to-end testing by triggering real events or sending test emails.

## Future Enhancements

1.  **Persistent State for Polling**: For Binance and IMAP, implement a persistent way (e.g., small DB, file) to store IDs of processed transactions/emails to robustly prevent duplicate alerts across bot restarts.
2.  **Advanced Email Parsing**: Use more sophisticated email parsing libraries or techniques if regex becomes too complex for UPI/HDFC emails.
3.  **More Notification Channels**: Support Slack, Discord, etc.
4.  **Admin Interface**: A simple web UI for status monitoring or configuration.
5.  **Scheduler**: Replace basic threading with a more robust scheduler like `APScheduler` for polling tasks.
