import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler
import logging

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Bot Token and Webhook URL
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"
WEBHOOK_URL = "https://test-1-ufqj.onrender.com/webhook"

# Initialize Telegram Bot application
application = Application.builder().token(BOT_TOKEN).build()

# Ensure application is initialized
application.initialize()

# Command Handler for `/start`
async def start(update: Update, context):
    """Handle the /start command."""
    await update.message.reply_text("Hello! I'm your bot. How can I assist you?")

# Add handlers to the bot
application.add_handler(CommandHandler("start", start))

@app.route("/webhook", methods=["POST"])
def webhook():
    """Webhook for Telegram bot."""
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))  # Process the update with asyncio.run
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Endpoint to set the webhook for Telegram bot."""
    try:
        application.bot.set_webhook(WEBHOOK_URL)
        return jsonify({"status": "webhook set"}), 200
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    # Run the Flask app
    app.run(host="0.0.0.0", port=5000)
