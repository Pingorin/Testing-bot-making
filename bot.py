import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from info import BOT_TOKEN, PHOTO_URL # info.py और script.py files वही रहेंगी
from script import START_TXT

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# /start command handler - यह वही रहेगा
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
    
    if PHOTO_URL:
        photo_to_send = PHOTO_URL 
    elif os.path.exists("photo.jpg"):
        photo_to_send = open("photo.jpg", 'rb')
    else:
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
    
    if not isinstance(photo_to_send, (str, bytes)):
        photo_to_send.close()


def main() -> None:
    """Start the bot in Polling Mode."""
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Register the command handler
    application.add_handler(CommandHandler("start", start))

    # --- POLLING MODE START ---
    logging.info("Starting bot with Polling Mode...")
    
    # run_polling() Telegram servers को updates के लिए check करता रहेगा
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    # --- POLLING MODE END ---


if __name__ == "__main__":
    main()
    
