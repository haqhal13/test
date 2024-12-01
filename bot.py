import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler
import logging
import traceback

# Enhanced Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Flask Application Setup
app = Flask(__name__)

# Bot Token and Webhook URL
BOT_TOKEN = "7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY"
WEBHOOK_URL = "https://test-1-ufqj.onrender.com/webhook"

# Initialize Telegram Application in async mode
application = Application.builder().token(BOT_TOKEN).build()

# Asynchronous Initialization
@app.before_first_request
async def initialize_bot():
    """Initialize the Telegram Application."""
    try:
        await application.initialize()
        logger.info("Telegram Application initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize Telegram Application!")
        logger.error(f"Error Details: {traceback.format_exc()}")

# Command Handler for `/start`
async def start(update: Update, context):
    """Reply to the /start command."""
    try:
        await update.message.reply_text("Hello! I am your bot, ready to assist!")
        logger.info(f"Responded to /start command from user: {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Error responding to /start command: {traceback.format_exc()}")

# Add Handlers to the Bot
application.add_handler(CommandHandler("start", start))

@app.route("/webhook", methods=["POST"])
async def webhook():
    """Handle incoming updates from Telegram."""
    try:
        # Parse update payload
        update_payload = request.get_json(force=True)
        logger.info(f"Received webhook update: {update_payload}")
        
        update = Update.de_json(update_payload, application.bot)
        await application.process_update(update)
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.error("Error occurred in webhook handler!")
        logger.error(f"Payload: {request.data}")
        logger.error(f"Error Details: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Set the Telegram bot webhook."""
    try:
        application.run_webhook(
            listen="0.0.0.0",
            port=5000,
            url_path="webhook",
            webhook_url=WEBHOOK_URL,
        )
        logger.info("Webhook set successfully!")
        return jsonify({"status": "webhook set"}), 200
    except Exception as e:
        logger.error("Failed to set webhook!")
        logger.error(f"Error Details: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    logger.info("Health check requested.")
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    try:
        # Ensure Flask uses an event loop compatible with async operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        logger.info("Starting Flask application...")
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        logger.critical("Flask application failed to start!")
        logger.critical(f"Error Details: {traceback.format_exc()}")
