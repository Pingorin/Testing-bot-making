from pyrogram import Client
from info import API_ID, API_HASH, BOT_TOKEN

class Bot(Client):
    def __init__(self):
        super().__init__(
            "telegram_bot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins") # plugins folder ko load karega
        )

    async def start(self):
        await super().start()
        print("Bot Started!")

    async def stop(self):
        await super().stop()
        print("Bot Stopped!")

# Client object banayein
app = Bot()
