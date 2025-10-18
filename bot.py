# File: bot.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# info.py और script.py से वेरिएबल्स इम्पोर्ट करें
from info import BOT_TOKEN, PHOTO_URL, CHANNEL_LINK
from script import START_TXT

# लॉगिंग सेटअप (एरर देखने के लिए)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start कमांड का फंक्शन
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    
    # इनलाइन बटन बनाने के लिए
    keyboard = [
        [InlineKeyboardButton("मेरा चैनल 🚀", url=CHANNEL_LINK)],
        [InlineKeyboardButton("डेवलपर से संपर्क करें 🧑‍💻", url="https://t.me/YourUsername")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # START_TXT में यूजर का नाम जोड़ने के लिए
    text = START_TXT.format(mention=user.mention_html())
    
    # फोटो, मैसेज और बटन एक साथ भेजना
    await update.message.reply_photo(
        photo=PHOTO_URL,
        caption=text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

# बॉट को चलाने के लिए मुख्य फंक्शन
def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    logger.info("बॉट स्टार्ट हो गया है...")
    application.run_polling()

if __name__ == '__main__':
    main()
    
