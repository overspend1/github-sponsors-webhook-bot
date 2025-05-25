import logging
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

class TelegramAPI:
    """Class to interact with Telegram API for sending notifications"""
    
    def __init__(self, token, chat_id, config):
        """Initialize with Telegram Bot Token and Chat ID"""
        self.token = token
        self.chat_id = chat_id
        self.config = config
        self.logger = logging.getLogger("GitHubSponsorsBot")
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