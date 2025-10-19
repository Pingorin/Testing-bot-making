import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ.get("API_ID", 12345))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")

# Database
DB_URI = os.environ.get("DB_URI", "your_mongodb_connection_string")
DB_NAME = os.environ.get("DB_NAME", "telegram_bot_db")

# /start command ke liye
START_PIC = os.environ.get("START_PIC", "https://example.com/your_photo.jpg")
BOT_LINK = os.environ.get("BOT_LINK", "https://t.me/YourBotUsername")
