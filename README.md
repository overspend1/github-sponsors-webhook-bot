# GitHub Sponsors & Multi-Source Payment Alert Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com/)

A versatile bot that sends instant Telegram notifications for:
- GitHub Sponsors payments.
- Binance cryptocurrency deposits and P2P payment receipts.
- UPI and HDFC Bank transactions (via email parsing).

Get real-time alerts with complete transaction details directly to your Telegram account.

![Multi-Source Payment Alert Bot](https://via.placeholder.com/800x400?text=Multi-Source+Payment+Alert+Bot)

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Option 1: Docker Installation](#option-1-docker-installation)
  - [Option 2: Manual Installation](#option-2-manual-installation)
- [Configuration](#-configuration)
  - [Environment Variables](#environment-variables)
  - [GitHub Webhook Setup (for GitHub Sponsors)](#github-webhook-setup-for-github-sponsors)
  - [Binance API Setup (for Binance Alerts)](#binance-api-setup-for-binance-alerts)
  - [IMAP Email Setup (for UPI/HDFC Alerts)](#imap-email-setup-for-upihdfc-alerts)
  - [Telegram Bot Setup](#telegram-bot-setup)
- [Usage](#-usage)
  - [Running the Bot](#running-the-bot)
  - [Testing the Webhook](#testing-the-webhook)
- [Deployment](#-deployment)
  - [Local Deployment](#local-deployment)
  - [Cloud Deployment](#cloud-deployment)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)
- [Performance Optimization](#-performance-optimization)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

- **Real-time GitHub Sponsors Notifications**: Immediate alerts for new GitHub sponsorships.
- **Binance Payment Alerts**:
    - Notifications for new cryptocurrency deposits.
    - Alerts for completed P2P payment receipts.
- **UPI & HDFC Bank Alerts (via Email Parsing)**:
    - Parses emails from a configured IMAP account to detect and notify about UPI and HDFC Bank transactions.
    - Customizable sender/subject filters for email identification.
- **Complete Transaction Details**: Get sponsor name, amount, tier, payment source, transaction IDs, and timestamps.
- **Secure Webhook Integration**: Verifies GitHub webhook signatures.
- **Secure Credential Management**: Uses environment variables for API keys and sensitive data.
- **Modular Design**: Payment sources are handled by separate modules for easy extension.
- **Docker Support**: Easy deployment with Docker.
- **Customizable**: Configure to meet your specific needs.
- **Lightweight**: Minimal resource requirements.
- **Open Source**: MIT licensed, free to use and modify.

## 📋 Prerequisites

Before you begin, ensure you have the following:

- Python 3.7 or higher
- A Telegram account
- Docker (optional, for containerized deployment)
- **For GitHub Sponsors Alerts**:
    - A GitHub account with Sponsors enabled.
    - A publicly accessible server to receive webhooks (or use a service like ngrok for testing).
- **For Binance Alerts (Optional)**:
    - A Binance account.
    - Binance API Key and Secret.
- **For UPI/HDFC Email Alerts (Optional)**:
    - An email account that receives UPI/HDFC payment notifications.
    - IMAP access details for that email account (host, port, username, password).

## 🔧 Installation

### Option 1: Docker Installation

The easiest way to get started is using Docker:

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/github-sponsors-webhook-bot.git
   cd github-sponsors-webhook-bot
   ```

2. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your credentials (see [Configuration](#-configuration) section).

4. Build and run the Docker container:
   ```bash
   docker build -t payment-alert-bot .
   docker run -d -p 5000:5000 --name payment-alert-bot --env-file .env payment-alert-bot
   ```

### Option 2: Manual Installation

If you prefer to run the bot without Docker:

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/github-sponsors-webhook-bot.git
   cd github-sponsors-webhook-bot
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv  # Or use 'python' if 'python3' is not available
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # You might need to install python-binance if not already included
   # pip install python-binance
   ```

4. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your credentials (see [Configuration](#-configuration) section).

6. Run the bot:
   ```bash
   python3 github_sponsors_bot.py # Or use 'python'
   ```

## ⚙️ Configuration

### Environment Variables

The bot requires various environment variables to be set in your `.env` file. Refer to the [`.env.example`](.env.example) file for a complete list and descriptions. Key variables include:

**Core:**
| Variable | Description | Example |
|----------|-------------|---------|
| `GITHUB_WEBHOOK_SECRET` | Secret for verifying GitHub webhook signatures (for Sponsors) | `your_webhook_secret` |
| `TELEGRAM_TOKEN` | Telegram Bot API token | `1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| `TELEGRAM_CHAT_ID` | Telegram chat ID to send notifications to | `123456789` |
| `WEBHOOK_HOST` | Host to bind the webhook server to (optional) | `0.0.0.0` |
| `WEBHOOK_PORT` | Port to bind the webhook server to (optional) | `5000` |

**Binance Alerts (Optional):**
| Variable | Description |
|----------|-------------|
| `BINANCE_API_KEY` | Your Binance API Key |
| `BINANCE_API_SECRET` | Your Binance API Secret |
| `BINANCE_POLL_INTERVAL` | Interval in seconds to poll Binance (default: 300) |

**IMAP Email Alerts (Optional - for UPI/HDFC):**
| Variable | Description |
|----------|-------------|
| `IMAP_HOST` | IMAP server hostname |
| `IMAP_PORT` | IMAP server port (default: 993 for SSL) |
| `IMAP_USER` | IMAP account username |
| `IMAP_PASSWORD` | IMAP account password |
| `IMAP_MAILBOX` | Mailbox to check (default: INBOX) |
| `IMAP_POLL_INTERVAL` | Interval in seconds to poll IMAP (default: 600) |
| `UPI_EMAIL_SENDER_FILTER` | Optional: Email address or keyword to filter UPI emails |
| `HDFC_EMAIL_SENDER_FILTER` | Optional: Email address or keyword to filter HDFC emails |

### GitHub Webhook Setup (for GitHub Sponsors)

1. Go to your GitHub repository or organization settings.
2. Navigate to "Webhooks" and click "Add webhook".
3. For the Payload URL, enter your server URL (e.g., `https://your-server.com/webhook/github`).
4. Set Content type to `application/json`.
5. Generate a secure random string for your webhook secret (e.g., `openssl rand -hex 20`).
6. Enter this secret in the "Secret" field on GitHub and in your `.env` file (`GITHUB_WEBHOOK_SECRET`).
7. Under "Which events would you like to trigger this webhook?", select "Let me select individual events".
8. Check only the "Sponsorships" option.
9. Ensure "Active" is checked and click "Add webhook".

### Binance API Setup (for Binance Alerts)

1. Log in to your Binance account.
2. Navigate to API Management (usually under your profile icon).
3. Create a new API key.
4. **Important Security Note**:
    - Grant only necessary permissions (e.g., "Enable Reading" for fetching transaction history). **Do NOT enable trading or withdrawal permissions unless absolutely necessary and you understand the risks.**
    - Consider restricting API key access to trusted IP addresses if possible.
5. Copy the API Key and Secret Key to your `.env` file (`BINANCE_API_KEY`, `BINANCE_API_SECRET`).

### IMAP Email Setup (for UPI/HDFC Alerts)

1. Ensure IMAP access is enabled for the email account you want to use.
2. Gather your IMAP server details:
    - IMAP Host (e.g., `imap.gmail.com`, `outlook.office365.com`)
    - IMAP Port (usually 993 for SSL/TLS, or 143 for non-SSL)
    - Your email username and password (or an app-specific password if your provider requires it, like Gmail with 2FA).
3. Enter these details into your `.env` file (`IMAP_HOST`, `IMAP_PORT`, `IMAP_USER`, `IMAP_PASSWORD`).
4. Specify the `IMAP_MAILBOX` (e.g., `INBOX`, or a specific folder where payment emails arrive).
5. Optionally, set `UPI_EMAIL_SENDER_FILTER` and `HDFC_EMAIL_SENDER_FILTER` to help the bot identify relevant emails. These can be sender email addresses (e.g., `alerts@hdfcbank.com`) or keywords expected in the subject/body.

**Note on Email Parsing**: The accuracy of UPI/HDFC alerts depends heavily on the consistency of email formats. The parsing logic in `payment_sources/imap_alerts.py` may need to be customized based on the specific emails you receive.

### Telegram Bot Setup

1. Open Telegram and search for [@BotFather](https://t.me/botfather).
2. Send the command `/newbot` and follow the instructions.
3. BotFather will provide you with a token (copy this to `TELEGRAM_TOKEN` in your `.env` file).
4. Start a chat with your new bot by clicking the link provided by BotFather.
5. To get your chat ID, start a chat with [@userinfobot](https://t.me/userinfobot).
6. The bot will reply with your account information, including your Chat ID.
7. Copy this Chat ID to `TELEGRAM_CHAT_ID` in your `.env` file.

## 🎮 Usage

### Running the Bot

Once configured, the bot will:

1. Start a webhook server listening for GitHub Sponsors events (if configured).
2. Initialize the Telegram bot.
3. Start polling threads for Binance and/or IMAP email alerts (if configured and enabled).
4. Send a startup message to your Telegram chat indicating active services.
5. Process incoming events/data and send notifications.

The bot logs its activity to both the console and a log file (`github_sponsors_bot.log`).

### Testing the Webhook

You can test the GitHub Sponsors webhook integration without setting up a real GitHub webhook by using the included test script:

```bash
python3 test_webhook.py # Or use 'python'
```

This will send a simulated GitHub Sponsors webhook event to your local server. If everything is set up correctly, you should receive a notification in your Telegram chat.

For testing with a real GitHub webhook but without exposing your local server to the internet, you can use [ngrok](https://ngrok.com/):

```bash
ngrok http 5000
```

Then update your GitHub webhook URL with the ngrok URL (e.g., `https://a1b2c3d4.ngrok.io/webhook/github`).

## 🚢 Deployment

### Local Deployment

For local development or personal use, you can run the bot directly on your machine:

```bash
python3 github_sponsors_bot.py # Or use 'python'
```

To keep the bot running after you close your terminal, use tools like `nohup` (Linux/macOS), `screen`/`tmux`, or Windows Task Scheduler.

### Cloud Deployment

For production use, deploying to a cloud provider is recommended. The Docker setup facilitates this. Examples include Heroku, AWS EC2, Digital Ocean Droplets. Ensure your environment variables are securely configured on the cloud platform.

## 🏗️ Architecture

The bot is designed with a modular architecture:
- **Main Application (`github_sponsors_bot.py`)**: Handles core logic, Flask web server for GitHub webhooks, Telegram bot initialization, and orchestration of polling threads.
- **Payment Source Modules (`payment_sources/`)**:
    - `binance_alerts.py`: Connects to Binance API, fetches payment data.
    - `imap_alerts.py`: Connects to IMAP server, fetches and parses emails for UPI/HDFC.
- **Configuration**: Managed via environment variables (`.env` file).

For more details, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 🔍 Troubleshooting

### Common Issues

- **Webhook Not Receiving Events (GitHub)**:
  - Verify server accessibility, webhook URL, server status, firewall.
  - Check GitHub webhook delivery logs.
- **Invalid Signature Errors (GitHub)**:
  - Match `GITHUB_WEBHOOK_SECRET` between GitHub and `.env`.
  - Ensure `application/json` content type.
- **Telegram Bot Not Sending Messages**:
  - Correct `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID`.
  - Ensure you've started a chat with the bot.
- **Binance/IMAP Alerts Not Working**:
  - Double-check API keys/credentials in `.env`.
  - Verify polling intervals and necessary permissions (Binance API, IMAP access).
  - Check logs for specific error messages from these modules.
  - For IMAP, ensure email filters (`UPI_EMAIL_SENDER_FILTER`, `HDFC_EMAIL_SENDER_FILTER`) are correctly set if used, and that the parsing logic in `imap_alerts.py` matches your email formats.
- **Docker Container Issues**:
  - Check Docker logs: `docker logs payment-alert-bot`.
  - Verify environment variables and port availability.

### Debugging

To enable more detailed logging, modify the logging level in `github_sponsors_bot.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    # ... rest of the config
)
```

## ⚡ Performance Optimization

- **Use HTTPS**: For GitHub webhook endpoint.
- **Efficient Polling**: Set reasonable `BINANCE_POLL_INTERVAL` and `IMAP_POLL_INTERVAL` to avoid excessive API/server load.
- **Production WSGI Server**: For production, use Gunicorn (included in Docker) or uWSGI.
- **Monitor Resources**: Keep an eye on CPU/memory.
- **Reverse Proxy**: Use Nginx or Apache for production deployments.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
