# GitHub Sponsors Webhook Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue)](https://www.docker.com/)

A webhook bot that sends instant Telegram notifications whenever you receive a payment through GitHub Sponsors. Get real-time alerts with complete transaction details directly to your Telegram account.

![GitHub Sponsors Webhook Bot](https://via.placeholder.com/800x400?text=GitHub+Sponsors+Webhook+Bot)

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Option 1: Docker Installation](#option-1-docker-installation)
  - [Option 2: Manual Installation](#option-2-manual-installation)
- [Configuration](#-configuration)
  - [Environment Variables](#environment-variables)
  - [GitHub Webhook Setup](#github-webhook-setup)
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

- **Real-time Notifications**: Receive immediate alerts when someone sponsors you on GitHub
- **Complete Transaction Details**: Get sponsor name, amount, tier selected, and timestamp
- **Secure Webhook Integration**: Verify webhook signatures for secure communication
- **Single-File Design**: All functionality in one Python file for simplicity
- **Docker Support**: Easy deployment with Docker
- **Customizable**: Configure to meet your specific needs
- **Lightweight**: Minimal resource requirements
- **Open Source**: MIT licensed, free to use and modify

## 📋 Prerequisites

Before you begin, ensure you have the following:

- Python 3.7 or higher
- A GitHub account with Sponsors enabled
- A Telegram account
- A publicly accessible server to receive webhooks (or use a service like ngrok for testing)
- Docker (optional, for containerized deployment)

## 🔧 Installation

### Option 1: Docker Installation

The easiest way to get started is using Docker:

1. Clone this repository:
   ```bash
   git clone https://github.com/overspend1/github-sponsors-webhook-bot.git
   cd github-sponsors-webhook-bot
   ```

2. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file with your credentials (see [Configuration](#-configuration) section)

4. Build and run the Docker container:
   ```bash
   docker build -t github-sponsors-bot .
   docker run -d -p 5000:5000 --name sponsors-bot --env-file .env github-sponsors-bot
   ```

### Option 2: Manual Installation

If you prefer to run the bot without Docker:

1. Clone this repository:
   ```bash
   git clone https://github.com/overspend1/github-sponsors-webhook-bot.git
   cd github-sponsors-webhook-bot
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file with your credentials (see [Configuration](#-configuration) section)

6. Run the bot:
   ```bash
   python github_sponsors_bot.py
   ```

## ⚙️ Configuration

### Environment Variables

The bot requires the following environment variables to be set in your `.env` file:

| Variable | Description | Example |
|----------|-------------|--------|
| `GITHUB_WEBHOOK_SECRET` | Secret for verifying GitHub webhook signatures | `your_webhook_secret` |
| `TELEGRAM_TOKEN` | Telegram Bot API token | `1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| `TELEGRAM_CHAT_ID` | Telegram chat ID to send notifications to | `123456789` |
| `WEBHOOK_HOST` | Host to bind the webhook server to (optional) | `0.0.0.0` |
| `WEBHOOK_PORT` | Port to bind the webhook server to (optional) | `5000` |

### GitHub Webhook Setup

1. Go to your GitHub repository or organization settings
2. Navigate to "Webhooks" and click "Add webhook"
3. For the Payload URL, enter your server URL (e.g., `https://your-server.com/webhook/github`)
4. Set Content type to `application/json`
5. Generate a secure random string to use as your webhook secret:
   ```bash
   openssl rand -hex 20
   ```
6. Enter this secret in the "Secret" field and in your `.env` file
7. Under "Which events would you like to trigger this webhook?", select "Let me select individual events"
8. Check only the "Sponsorships" option
9. Ensure "Active" is checked and click "Add webhook"

### Telegram Bot Setup

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send the command `/newbot` and follow the instructions
3. BotFather will provide you with a token (copy this to your `.env` file)
4. Start a chat with your new bot by clicking the link provided by BotFather
5. To get your chat ID, start a chat with [@userinfobot](https://t.me/userinfobot)
6. The bot will reply with your account information, including your Chat ID
7. Copy this Chat ID to your `.env` file

## 🎮 Usage

### Running the Bot

Once configured, the bot will:

1. Start a webhook server listening for GitHub events
2. Initialize the Telegram bot
3. Send a startup message to your Telegram chat
4. Process incoming webhook events and send notifications

The bot logs its activity to both the console and a log file (`github_sponsors_bot.log`).

### Testing the Webhook

You can test the webhook integration without setting up a real GitHub webhook by using the included test script:

```bash
python test_webhook.py
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
python github_sponsors_bot.py
```

To keep the bot running after you close your terminal, you can use tools like:

- `nohup` on Linux/macOS:
  ```bash
  nohup python github_sponsors_bot.py &
  ```
- `screen` or `tmux` for terminal sessions:
  ```bash
  screen -S sponsors-bot
  python github_sponsors_bot.py
  # Press Ctrl+A, D to detach
  ```
- Windows Task Scheduler for Windows systems

### Cloud Deployment

For production use, we recommend deploying to a cloud provider:

#### Heroku

1. Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
2. Login and create a new app:
   ```bash
   heroku login
   heroku create your-app-name
   ```
3. Set environment variables:
   ```bash
   heroku config:set GITHUB_WEBHOOK_SECRET=your_secret
   heroku config:set TELEGRAM_TOKEN=your_telegram_token
   heroku config:set TELEGRAM_CHAT_ID=your_chat_id
   ```
4. Deploy the app:
   ```bash
   git push heroku main
   ```
5. Update your GitHub webhook URL to `https://your-app-name.herokuapp.com/webhook/github`

#### AWS

1. Create an EC2 instance
2. Install Docker on the instance
3. Clone the repository and build the Docker image
4. Run the container with your environment variables
5. Set up a load balancer or Elastic IP for a stable endpoint
6. Update your GitHub webhook URL with your instance's public address

#### Digital Ocean

1. Create a Droplet
2. Install Docker on the Droplet
3. Clone the repository and build the Docker image
4. Run the container with your environment variables
5. Set up a Floating IP for a stable endpoint
6. Update your GitHub webhook URL with your Droplet's public address

## 🏗️ Architecture

The bot is designed with a simple, single-file architecture for ease of understanding and maintenance. For more details on the architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

Key components:

1. **Flask Web Server**: Handles incoming webhook requests
2. **Webhook Handler**: Verifies and processes GitHub webhook events
3. **Telegram Bot**: Sends notifications to your Telegram chat

## 🔍 Troubleshooting

### Common Issues

#### Webhook Not Receiving Events

- **Problem**: GitHub webhook events aren't being received by your server.
- **Solutions**:
  - Verify your server is publicly accessible
  - Check that the webhook URL in GitHub settings is correct
  - Ensure your server is running and listening on the correct port
  - Check firewall settings to allow incoming connections
  - Look at GitHub webhook delivery logs for error details

#### Invalid Signature Errors

- **Problem**: Webhook requests are being rejected due to invalid signatures.
- **Solutions**:
  - Verify the webhook secret in your `.env` file matches the one in GitHub settings
  - Ensure the webhook payload is not being modified in transit (use HTTPS)
  - Check that the content type is set to `application/json` in GitHub webhook settings

#### Telegram Bot Not Sending Messages

- **Problem**: Notifications aren't being sent to Telegram.
- **Solutions**:
  - Confirm your bot token is correct
  - Ensure you've started a conversation with your bot
  - Verify your chat ID is correct
  - Check if the bot has been blocked or deleted
  - Look at the bot logs for error messages

#### Docker Container Issues

- **Problem**: Docker container won't start or crashes.
- **Solutions**:
  - Check Docker logs: `docker logs sponsors-bot`
  - Verify environment variables are set correctly
  - Ensure the required ports are available
  - Check for permission issues

### Debugging

To enable more detailed logging, you can modify the logging level in `github_sponsors_bot.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('github_sponsors_bot.log')
    ]
)
```

## ⚡ Performance Optimization

For optimal performance:

1. **Use HTTPS**: Always use HTTPS for your webhook endpoint to ensure secure communication.
2. **Minimize Response Time**: The webhook handler should process events quickly to avoid timeouts.
3. **Use a Production WSGI Server**: For production deployments, use Gunicorn (included in the Docker setup) or uWSGI instead of Flask's development server.
4. **Monitor Resource Usage**: Keep an eye on CPU and memory usage, especially for high-traffic repositories.
5. **Implement Rate Limiting**: If you expect a high volume of sponsorships, consider implementing rate limiting for Telegram notifications.
6. **Use a Reverse Proxy**: For production deployments, use Nginx or Apache as a reverse proxy in front of the application.

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.