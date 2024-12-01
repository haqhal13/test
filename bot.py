import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Constants
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"
WEBHOOK_URL = "https://test-1-ufqj.onrender.com/webhook"

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram Application with asynchronous support
application = (
    Application.builder().token(BOT_TOKEN).arbitrary_callback_data(True).build()
)

# Telegram bot command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text("Welcome! Your bot is active and ready.")

async def echo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo back any message sent by the user."""
    await update.message.reply_text(update.message.text)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update caused error {context.error}")

# Configure Telegram handlers
def configure_handlers():
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_message))
    application.add_error_handler(error_handler)

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return "Bot is healthy and running!", 200

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook_handler():
    """Handle incoming webhook requests."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.create_task(application.process_update(update))
        return "OK", 200
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return jsonify({"error": str(e)}), 500

# Main entry point
if __name__ == "__main__":
    # Configure Telegram bot handlers
    configure_handlers()

    # Set up Telegram webhook
    logger.info("Setting webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path="/webhook",
        webhook_url=WEBHOOK_URL,
    )

    # Run Flask app for health checks
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), threaded=True)
