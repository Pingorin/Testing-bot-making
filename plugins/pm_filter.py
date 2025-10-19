from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from info import START_PIC, BOT_LINK
from script import Script
from database.ia_filter import add_file, find_files, get_file_by_id

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

# /index command handler
@Client.on_message(filters.command("index") & filters.private)
async def index_command(client, message: Message):
    # User se channel ka last message forward karne ko kahein
    await message.reply_text("Kripya us channel ka koi bhi ek message yahaan forward karein jise aap index karna chahte hain.")

# Forwarded message handler (indexing shuru karne ke liye)
@Client.on_message(filters.private & filters.forwarded)
async def handle_forwarded(client, message: Message):
    if not message.forward_from_chat:
        await message.reply_text("Yeh ek valid forwarded message nahi lag raha hai.")
        return

    channel_id = message.forward_from_chat.id
    
    try:
        total_files = await client.get_chat_history_count(channel_id)
        
        await message.reply_text(
            Script.INDEX_START_TXT.format(total=total_files),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Indexing Start", callback_data=f"index_start_{channel_id}")]
                ]
            )
        )
    except Exception as e:
        await message.reply_text(f"Error: {e}. Kya main us channel ka admin hoon?")

# Indexing Start button handler
@Client.on_callback_query(filters.regex(r"^index_start_"))
async def start_indexing(client, query):
    channel_id = int(query.data.split("_")[-1])
    
    await query.message.edit_text("Indexing shuru ho rahi hai...")
    
    saved = 0
    duplicate = 0
    unsupported = 0
    current = 0
    
    async for msg in client.get_chat_history(channel_id):
        current += 1
        
        # Har 100 files par progress update karein
        if current % 100 == 0:
            try:
                await query.message.edit_text(
                    Script.INDEX_PROGRESS_TXT.format(
                        total="N/A", # Total count yahan simplify kiya gaya hai
                        current=current,
                        saved=saved,
                        duplicate=duplicate,
                        unsupported=unsupported
                    )
                )
            except:
                pass # Message not modified error ko ignore karein
        
        # Check karein ki message mein file (document, video, audio) hai ya nahi
        if msg.media:
            file_name = None
            file_id = None
            file_unique_id = None

            if msg.document:
                file_name = msg.document.file_name
                file_id = msg.document.file_id
                file_unique_id = msg.document.file_unique_id
            elif msg.video:
                file_name = msg.video.file_name or "video_file"
                file_id = msg.video.file_id
                file_unique_id = msg.video.file_unique_id
            # Aap audio aur photo ke liye bhi add kar sakte hain

            if file_name:
                status = await add_file(file_id, file_unique_id, file_name, msg.caption)
                if status == "saved":
                    saved += 1
                elif status == "duplicate":
                    duplicate += 1
            else:
                unsupported += 1
        else:
            unsupported += 1
            
    await query.message.edit_text(f"Indexing poori hui!\nSaved: {saved}\nDuplicate: {duplicate}\nUnsupported: {unsupported}")


# Search handler (Group aur PM dono ke liye)
@Client.on_message(filters.text & (filters.private | filters.group) & ~filters.command())
async def search_query(client, message: Message):
    query_txt = message.text
    
    # 3. Spelling Check (Basic) - Aap yahaan pyspellchecker ka istemaal kar sakte hain
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
