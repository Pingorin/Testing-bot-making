import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from info import BOT_TOKEN
from script import START_TXT # Assuming START_TXT is still imported

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Render Environment Variables
# Render Web Service हमेशा 0.0.0.0 पर listen करेगा।
PORT = int(os.environ.get('PORT', 8080))
WEBHOOK_URL = os.environ.get('RENDER_EXTERNAL_URL', None) 
# Note: Render `RENDER_EXTERNAL_URL` नाम का env var देता है, 
# जो आपकी service का public URL होता है।
if WEBHOOK_URL and not WEBHOOK_URL.endswith('/'):
    WEBHOOK_URL += '/'


# /start command handler (यह वही रहेगा)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # ... (Inline Keyboard और Photo भेजने का code वही रहेगा)
    
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
    
    # Assuming PHOTO_URL is also handled in info.py or env
    photo_to_send = os.environ.get("PHOTO_URL") if os.environ.get("PHOTO_URL") else "photo.jpg" 

    try:
        # File/URL handling logic for demonstration
        if photo_to_send.startswith('http'):
            # Send using URL
            await update.message.reply_photo(
                photo=photo_to_send,
                caption=START_TXT,
                reply_markup=reply_markup
            )
        else:
            # Send using local file
            with open(photo_to_send, 'rb') as photo_file:
                 await update.message.reply_photo(
                    photo=photo_file,
                    caption=START_TXT,
                    reply_markup=reply_markup
                )
    except Exception as e:
        logging.error(f"Error sending photo: {e}")
        await update.message.reply_text(
            "Photo not found or failed to load! Sending text only.\n\n" + START_TXT, 
            reply_markup=reply_markup
        )
        

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # --- WEBHOOK MODE START ---
    if WEBHOOK_URL:
        # Render deployment (Web Service)
        logging.info(f"Starting Webhook on port {PORT} at URL: {WEBHOOK_URL}{BOT_TOKEN}")
        
        # Webhook URL Path के रूप में BOT_TOKEN का उपयोग करना secure है
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=f"{WEBHOOK_URL}{BOT_TOKEN}"
        )
    else:
        # Local development (Polling Mode)
        logging.info("WEBHOOK_URL not set. Falling back to Polling for local development.")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    # --- WEBHOOK MODE END ---


if __name__ == "__main__":
    main()
        
