from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from info import START_PIC, BOT_LINK
from script import Script

# /start command handler (only in private chat)
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    await message.reply_photo(
        photo=START_PIC,
        caption=Script.START_TXT.format(mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Bot Link", url=BOT_LINK)]
            ]
        )
    )

# /help or other commands can go here later
