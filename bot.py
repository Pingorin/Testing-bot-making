import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from info import BOT_TOKEN, PHOTO_URL
from script import START_TXT

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# For Render deployment, we use the port from environment variables
PORT = int(os.environ.get('PORT', 8080))
# The URL where your bot is hosted (Render provides this)
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a photo, the welcome message, and an inline keyboard on /start."""
    
    # 1. Inline Keyboard (Buttons with Links)
    keyboard = [
        [
            InlineKeyboardButton("YouTube Channel", url="https://youtube.com/your_channel"),
            InlineKeyboardButton("Official Website", url="https://example.com"),
        ],
        [
            InlineKeyboardButton("Contact Developer", url="https://t.me/your_username"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 2. Send Photo and Message
    
    # Check if we are using a local file or a direct URL for the photo
    if PHOTO_URL:
        # Use a publicly accessible URL if defined in info.py (for easy testing/deployment)
        photo_to_send = PHOTO_URL 
    elif os.path.exists("photo.jpg"):
        # Use local file if it exists
        photo_to_send = open("photo.jpg", 'rb')
    else:
        # Fallback if no photo is found
        await update.message.reply_text(
            "Photo not found! Sending text only.\n\n" + START_TXT, 
            reply_markup=reply_markup
        )
        return

    # Send the photo with the START_TXT as caption
    await update.message.reply_photo(
        photo=photo_to_send,
        caption=START_TXT,
        reply_markup=reply_markup
    )

    # Close the file handle if a local file was used
    if isinstance(photo_to_send, (str, bytes)): # Check if it's not an open file object
        pass
    else:
        photo_to_send.close()


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Register the command handler
    application.add_handler(CommandHandler("start", start))

    # Deployment logic for Render (using Webhooks)
    if WEBHOOK_URL:
        logging.info(f"Starting bot with Webhook at port {PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"
        )
    else:
        # Local development (using Polling)
        logging.info("Starting bot with Polling (for local development)")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

