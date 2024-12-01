import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
BOT_TOKEN = '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY'
WEBHOOK_URL = "https://test-1-ufqj.onrender.com/webhook"

# Flask app
app = Flask(__name__)

# Telegram application instance
application = Application.builder().token(BOT_TOKEN).build()

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return "Bot is running!", 200


@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handle incoming webhook POST requests."""
    try:
        # Parse incoming update
        update = Update.de_json(request.get_json(), application.bot)
        # Process update asynchronously
        application.create_task(application.process_update(update))
        return "OK", 200
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return jsonify({"error": str(e)}), 500


# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text("Welcome! I am your bot.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo back user messages."""
    await update.message.reply_text(update.message.text)


# Error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")


# Initialize bot
def configure_telegram_bot():
    """Add handlers to the bot and set webhook."""
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    # Set the webhook
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path="/webhook",
        webhook_url=WEBHOOK_URL,
    )


if __name__ == "__main__":
    # Configure bot handlers and start the webhook
    configure_telegram_bot()

    # Start Flask app
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), threaded=True)
