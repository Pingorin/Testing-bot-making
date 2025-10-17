import os
from dotenv import load_dotenv

# Load environment variables from a .env file (for local testing)
load_dotenv() 

# 1. BOT TOKEN
# Get your token from @BotFather on Telegram and set it as an environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# 2. PHOTO URL (Optional)
# If you want to use a direct public image URL instead of a local 'photo.jpg' file, 
# you can define it here or in your environment variables.
PHOTO_URL = os.environ.get("PHOTO_URL", None)

# Note: PRODUCTION deployment (जैसे Render) में, आपको BOT_TOKEN को environment variable 
# के रूप में set करना होगा।
