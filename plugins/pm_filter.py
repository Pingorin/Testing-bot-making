from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from info import START_PIC, BOT_LINK
from script import Script
from database.ia_filter import find_files, get_file_by_id
# from pyspellchecker import SpellChecker # Uncomment agar spelling check use karna hai

# /start command handler
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

# Search handler (Group aur PM dono ke liye)
@Client.on_message(filters.text & (filters.private | filters.group) & ~filters.command())
async def search_query(client, message: Message):
    query_txt = message.text
    
    # 3. Spelling Check (Basic) 
    # spell = SpellChecker()
    # corrected_query = spell.correction(query_txt)
    # if corrected_query != query_txt:
    #     await message.reply_text(f"Kya aapka matlab tha: `{corrected_query}`?")
    
    # 4. Files search karna
    files, total_results = await find_files(query_txt, max_results=10, page=0)
    
    if not files:
        await message.reply_text("Aisi koi file nahi mili.")
        return

    buttons = []
    for file in files:
        # File name ko 50 characters tak limit karein
        file_name = file.get('file_name', 'No Name')[:50]
        buttons.append([InlineKeyboardButton(file_name, callback_data=f"getfile_{file['file_id']}")])
    
    # Pagination buttons
    if total_results > 10:
        buttons.append(
            [
                # Back button (disabled on page 0)
                # InlineKeyboardButton("Back", callback_data="page_back_0"), 
                InlineKeyboardButton(f"Page 1/{(total_results // 10) + 1}", callback_data="noop"),
                InlineKeyboardButton("Next", callback_data=f"page_next_1_{query_txt}")
            ]
        )
        
    await message.reply_text(f"Total {total_results} files mili.", reply_markup=InlineKeyboardMarkup(buttons))

# 5. File bhejme ka handler
@Client.on_callback_query(filters.regex(r"^getfile_"))
async def get_file_handler(client, query):
    file_id = query.data.split("_")[-1]
    
    file_info = await get_file_by_id(file_id)
    if not file_info:
        await query.answer("File not found in database.", show_alert=True)
        return
        
    try:
        # User ko PM mein file bhejें
        await client.send_document(
            chat_id=query.from_user.id,
            document=file_id,
            caption=file_info.get('caption', ''),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Join Channel", url="https://t.me/your_channel_link")]
                ]
            )
        )
        await query.answer("File aapke PM mein bhej di gayi hai!", show_alert=True)
    except Exception as e:
        await query.answer(f"Error: {e}. Kya aapne bot ko PM mein start kiya hai?", show_alert=True)

# (Aapko pagination ("page_next_") ke liye bhi callback handler banana hoga)
