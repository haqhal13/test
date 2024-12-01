import os
from flask import Flask
from threading import Thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

# Bot Token (replace with your actual token)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7739378344:AAHePCaShSC60pN1VwX9AY4TqD-xZMxQ1gY')

# Flask app for health check
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return "OK", 200

# Start Command Handler
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

# Payment Method Handlers
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
            [
                InlineKeyboardButton(
                    "1 Month (£6.75)",
                    web_app=WebAppInfo(url="https://buy.stripe.com/8wM0041QI3xK3ficMP"),
                )
            ],
            [
                InlineKeyboardButton(
                    "Lifetime (£10)",
                    web_app=WebAppInfo(url="https://buy.stripe.com/aEUeUYaneecoeY03cc"),
                )
            ],
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

    elif query.data == "i_paid":
        await query.edit_message_text(
            text="Thank you! Please send a screenshot of your payment or provide the transaction ID for verification.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Go Back", callback_data="go_back")]
            ])
        )

# Go Back Handler
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

# Main Function
def main():
    # Telegram bot setup
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(payment_handler, pattern="^(paypal|apple_google_pay|crypto|i_paid)$"))
    application.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))

    # Set webhook URL
    WEBHOOK_URL = f"https://<your-app-name>.onrender.com/{BOT_TOKEN}"  # Replace <your-app-name> with your Render app name
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        json={"url": WEBHOOK_URL},
    )
    print("Webhook set:", response.status_code, response.text)

    # Flask thread for health checks
    thread = Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
    thread.start()

    # Telegram webhook
    port = int(os.environ.get("PORT", 8443))
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
