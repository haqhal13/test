import os
from flask import Flask, request
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

# Bot Token and Webhook URL
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY')
WEBHOOK_URL = "https://test-1-ufqj.onrender.com/webhook"  # Replace with your Render app link

# Flask app for webhook and health checks
app = Flask(__name__)

# Initialize Telegram application globally
application = Application.builder().token(BOT_TOKEN).build()

# Telegram webhook route
@app.route('/webhook', methods=['POST'])
def webhook_handler():
    try:
        # Log incoming request
        print("Incoming webhook payload:", request.json)

        # Process the Telegram update
        application.update_queue.put(Update.de_json(request.json, application.bot))
        return "OK", 200
    except Exception as e:
        # Log the error
        print("Error in webhook handler:", str(e))
        return "Internal Server Error", 500

# Health check route
@app.route('/health', methods=['GET'])
def health_check():
    return "Bot is running!", 200

# Default route (optional)
@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Telegram Bot Service!", 200

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    intro_text = (
        "👋 Welcome to the VIP Payment Bot!\n\n"
        "💎 Choose your subscription plan below to proceed:\n\n"
        "1 Month: £6.75\n"
        "Lifetime: £10"
    )
    keyboard = [
        [InlineKeyboardButton("PayPal", callback_data="paypal")],
        [InlineKeyboardButton("Apple Pay / Google Pay", callback_data="apple_google_pay")],
        [InlineKeyboardButton("Crypto (No KYC)", callback_data="crypto")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(intro_text, reply_markup=reply_markup)

# Payment method handler
async def payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    if query.data == "paypal":
        await query.edit_message_text(
            text="Send payment to:\n\n"
                 "💳 PayPal: onlyvipfan@outlook.com\n\n"
                 "💎 Pricing:\n"
                 "1 Month: £6.75\n"
                 "Lifetime: £10\n\n"
                 "✅ MUST BE FRIENDS AND FAMILY\n"
                 "❌ DO NOT LEAVE A NOTE\n\n"
                 "After payment, click 'I Paid' and provide your PayPal email.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Go Back", callback_data="go_back")]
            ])
        )
    elif query.data == "apple_google_pay":
        keyboard = [
            [InlineKeyboardButton("1 Month (£6.75)", url="https://buy.stripe.com/8wM0041QI3xK3ficMP")],
            [InlineKeyboardButton("Lifetime (£10)", url="https://buy.stripe.com/aEUeUYaneecoeY03cc")],
            [InlineKeyboardButton("Go Back", callback_data="go_back")],
        ]
        await query.edit_message_text(
            text="💳 Pay using Apple Pay / Google Pay via the links below:\n\n"
                 "💎 Pricing:\n"
                 "1 Month: £6.75\n"
                 "Lifetime: £10",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif query.data == "crypto":
        await query.edit_message_text(
            text="Send crypto to the following address:\n\n"
                 "💰 Bitcoin: 1ExampleBTCAddress\n"
                 "💰 Ethereum: 0xExampleETHAddress\n\n"
                 "💎 Pricing:\n"
                 "1 Month: $8\n"
                 "Lifetime: $14\n\n"
                 "After payment, click 'I Paid'.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Go Back", callback_data="go_back")]
            ])
        )

# Go back handler
async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    intro_text = (
        "👋 Welcome to the VIP Payment Bot!\n\n"
        "💎 Choose your subscription plan below to proceed:\n\n"
        "1 Month: £6.75\n"
        "Lifetime: £10"
    )
    keyboard = [
        [InlineKeyboardButton("PayPal", callback_data="paypal")],
        [InlineKeyboardButton("Apple Pay / Google Pay", callback_data="apple_google_pay")],
        [InlineKeyboardButton("Crypto (No KYC)", callback_data="crypto")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.edit_message_text(intro_text, reply_markup=reply_markup)

# Main function
def main():
    # Add command and callback query handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(payment_handler, pattern="^(paypal|apple_google_pay|crypto)$"))
    application.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))

    # Set up the webhook
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        json={"url": WEBHOOK_URL},
    )
    print("Webhook set:", response.status_code, response.text)

    # Start Flask in a separate thread
    flask_thread = Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
    flask_thread.start()

    # Start the Telegram bot
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path="webhook",
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
