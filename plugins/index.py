from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from script import Script
from database.ia_filter import add_file

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
  
