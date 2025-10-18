# bot.py

import math
import os
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from spellchecker import SpellChecker

from info import API_ID, API_HASH, BOT_TOKEN
from script import Script
from database import db
import pm_filter # pm_filter.py को इम्पोर्ट करें ताकि उसके हैंडलर रजिस्टर हो जाएं

# स्पेल चेकर को इनिशियलाइज़ करें
spell = SpellChecker()

# Pyrogram Client
app = Client(
    "FilterBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Flask Web App (Render के लिए)
web_app = Flask(__name__)
@web_app.route('/')
def hello_world():
    return 'Bot is running!'

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    await message.reply_photo(
        photo="https://telegra.ph/file/1832ab23f2733c53641a4.jpg",
        caption=Script.START_TXT.format(mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔗 डेवलपर से संपर्क करें", url="https://t.me/your_username")]]
        )
    )

@app.on_message(filters.text & (filters.private | filters.group))
async def search_handler(client, message: Message):
    query = message.text
    words = query.split()
    corrected_words = [spell.correction(word) for word in words if spell.correction(word)]
    corrected_query = " ".join(corrected_words)
    
    search_term = corrected_query if corrected_query else query

    files, total_results = await db.find_files(search_term)

    if not files:
        if corrected_query and query != corrected_query:
            return await message.reply_text(f"कोई परिणाम नहीं मिला।\nक्या आपका मतलब था: `{corrected_query}`?")
        return await message.reply_text("माफ़ करें, कोई परिणाम नहीं मिला। 😟")

    buttons = []
    for file in files:
        buttons.append([
            InlineKeyboardButton(
                text=f"📂 {file['file_name']} ({get_size(file['file_size'])})",
                callback_data=f"getfile_{file['_id']}"
            )
        ])

    total_pages = math.ceil(total_results / 10)
    if total_pages > 1:
        buttons.append([
            InlineKeyboardButton("⏪", callback_data="dummy"),
            InlineKeyboardButton(f"1/{total_pages}", callback_data="dummy"),
            InlineKeyboardButton("⏩", callback_data=f"next_1_{search_term}")
        ])

    await message.reply_text(
        f"**'{query}' के लिए {total_results} परिणाम मिले:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex(r"^(next|back)_(\d+)_(.*)"))
async def pagination_handler(client, query):
    action, page_str, search_query = query.matches[0].groups()
    page = int(page_str)

    if action == "next": new_page = page + 1
    else: new_page = page - 1

    files, total_results = await db.find_files(search_query, page=new_page)
    
    buttons = []
    for file in files:
        buttons.append([
            InlineKeyboardButton(
                text=f"📂 {file['file_name']} ({get_size(file['file_size'])})",
                callback_data=f"getfile_{file['_id']}"
            )
        ])

    total_pages = math.ceil(total_results / 10)
    page_buttons = []
    if new_page > 1:
        page_buttons.append(InlineKeyboardButton("⏪", callback_data=f"back_{new_page-1}_{search_query}"))
    
    page_buttons.append(InlineKeyboardButton(f"{new_page}/{total_pages}", callback_data="dummy"))

    if new_page < total_pages:
        page_buttons.append(InlineKeyboardButton("⏩", callback_data=f"next_{new_page+1}_{search_query}"))
    
    buttons.append(page_buttons)
    await query.message.edit_reply_markup(InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex(r"^getfile_"))
async def get_file_handler(client, query):
    file_id = query.data.split("_")[1]
    file_info = await db.get_file(file_id)

    if not file_info:
        return await query.answer("फाइल नहीं मिली!", show_alert=True)

    try:
        await client.copy_message(
            chat_id=query.from_user.id,
            from_chat_id=file_info['chat_id'],
            message_id=file_info['message_id'],
            caption=file_info.get('caption', ''),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 चैनल से जुड़ें", url="https://t.me/your_channel")]]
            )
        )
        await query.answer("फाइल आपके प्राइवेट मैसेज में भेज दी गई है। ✅", show_alert=False)
    except Exception as e:
        await query.answer(f"त्रुटि: {e}", show_alert=True)

def get_size(size_bytes):
    if size_bytes == 0: return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

# बॉट को एक अलग थ्रेड में चलाने के लिए
def run_bot():
    app.run()

if __name__ == "__main__":
    # बॉट को बैकग्राउंड में शुरू करें
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # यह हिस्सा केवल लोकल टेस्टिंग के लिए है। Render पर Gunicorn इसे हैंडल करेगा।
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)
    
