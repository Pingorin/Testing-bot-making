# bot.py

import math
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from spellchecker import SpellChecker

from info import API_ID, API_HASH, BOT_TOKEN, ADMINS, LOG_CHANNEL
from script import Script
from database import db
import pm_filter # pm_filter.py को इम्पोर्ट करें

# Spell checker को इनिशियलाइज़ करें
spell = SpellChecker()

# Pyrogram Client
app = Client(
    "FilterBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    """/start कमांड हैंडलर"""
    await message.reply_photo(
        photo="https://telegra.ph/file/1832ab23f2733c53641a4.jpg", # आप अपनी फोटो का लिंक डाल सकते हैं
        caption=Script.START_TXT.format(mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("Developer", url="https://t.me/your_username")]]
        )
    )

@app.on_message(filters.text & (filters.private | filters.group))
async def search_handler(client, message: Message):
    """ग्रुप और PM में सर्च को हैंडल करता है"""
    query = message.text
    
    # स्पेलिंग चेक और सुधार
    words = query.split()
    corrected_words = [spell.correction(word) for word in words]
    corrected_query = " ".join(filter(None, corrected_words))

    if not corrected_query:
        return

    # डेटाबेस से फाइलें खोजें
    files, total_results = await db.find_files(corrected_query)

    if not files:
        if query != corrected_query:
            return await message.reply_text(f"कोई परिणाम नहीं मिला।\nक्या आपका मतलब था: `{corrected_query}`?")
        else:
            return await message.reply_text("कोई परिणाम नहीं मिला।")

    # बटन बनाएं
    buttons = []
    for file in files:
        buttons.append([
            InlineKeyboardButton(
                text=f"📂 {file['file_name']} ({get_size(file['file_size'])})",
                callback_data=f"getfile_{file['_id']}"
            )
        ])

    # पेजिंग बटन
    total_pages = math.ceil(total_results / 10)
    if total_pages > 1:
        buttons.append([
            InlineKeyboardButton("⏪", callback_data="dummy"),
            InlineKeyboardButton(f"1/{total_pages}", callback_data="dummy"),
            InlineKeyboardButton("⏩", callback_data=f"next_1_{corrected_query}")
        ])

    await message.reply_text(
        f"**'{query}' के लिए {total_results} परिणाम मिले:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex(r"^next_|^back_"))
async def pagination_handler(client, query):
    """पेजिंग बटन को हैंडल करता है"""
    try:
        data = query.data.split("_")
        action = data[0]
        page = int(data[1])
        search_query = "_".join(data[2:])
        
        if action == "next":
            new_page = page + 1
        elif action == "back":
            new_page = page - 1
        else:
            return

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

    except Exception as e:
        print(e) # लॉगिंग के लिए

@app.on_callback_query(filters.regex(r"^getfile_"))
async def get_file_handler(client, query):
    """जब यूजर फाइल लिंक बटन पर क्लिक करता है"""
    file_id = query.data.split("_")[1]
    
    file_info = await db.get_file(file_id)
    if not file_info:
        return await query.answer("फाइल नहीं मिली!", show_alert=True)

    try:
        # यूजर को PM में फाइल भेजें
        await client.copy_message(
            chat_id=query.from_user.id,
            from_chat_id=file_info['chat_id'],
            message_id=file_info['message_id'],
            caption=file_info.get('caption', ''),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔗 चैनल से जुड़ें", url="https://t.me/your_channel")]]
            )
        )
        await query.answer("फाइल आपके PM में भेज दी गई है।", show_alert=True)
    except Exception as e:
        await query.answer(f"त्रुटि: {e}", show_alert=True)


def get_size(size_bytes):
    """फाइल साइज को पढ़ने योग्य फॉर्मेट में बदलता है"""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

print("बॉट शुरू हो रहा है...")
app.run()
                             
