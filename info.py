# info.py

import os
from dotenv import load_dotenv

load_dotenv() 

# 1. BOT TOKEN (Required)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# 2. PHOTO URL (Optional)
PHOTO_URL = os.environ.get("PHOTO_URL", None)

# 3. RENDER ENVIRONMENT VARIABLES (Render खुद सेट करेगा)
# Render Web Services के लिए $PORT और $WEBHOOK_URL चाहिए।
# हम इन्हें सीधे bot.py में os.environ से उठाएंगे।
