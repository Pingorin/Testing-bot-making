# info.py

import os

# Telegram API Credentials
API_ID = int(os.environ.get("API_ID", 123456))  # अपना API ID यहाँ डालें
API_HASH = os.environ.get("API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e") # अपना API HASH यहाँ डालें
BOT_TOKEN = os.environ.get("BOT_TOKEN", "50a04ab22e0b3552dd351028a6d1a1c4") # अपना BOT TOKEN यहाँ डालें

# Database
DB_URI = os.environ.get("DB_URI", "mongodb://<user>:<password>@<host>:<port>/<db_name>") # अपना MongoDB Connection String यहाँ डालें

# Other
ADMINS = [int(admin) for admin in os.environ.get("ADMINS", "123456789").split()] # अपनी Telegram User ID यहाँ डालें
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-100xxxxxxxxx")) # Log भेजने के लिए चैनल ID
