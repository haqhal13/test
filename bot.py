import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token
BOT_TOKEN = '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY'

# Initialize Flask app
app = Flask(__name__)

# Telegram Application instance
application = None


@app.route('/health', methods=['GET'])
def health_check():
    return "Bot is running!", 200


@app.route('/webhook', methods=['POST'])
async def webhook_handler():
    global application
    try:
        # Parse incoming update from Telegram
        update = Update.de_json(request.json, application.bot)
        await application.process_update(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return jsonify({"error": str(e)}), 500


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text("Welcome! I am your bot.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo user messages."""
    await update.message.reply_text(f"You said: {update.message.text}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log the error caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Main function to set up webhook and handlers."""
    global application

    # Initialize Telegram application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_error_handler(error_handler)

    # Start the webhook
    WEBHOOK_URL = "https://test-1-ufqj.onrender.com/webhook"
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
    )


if __name__ == "__main__":
    # Start Flask in a thread
    from threading import Thread
    flask_thread = Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8443))))
    flask_thread.start()

    # Initialize Telegram application
    main()
