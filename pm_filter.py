# pm_filter.py

import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait

from info import ADMINS
from database import db

indexing_status = {}

@Client.on_message(filters.command("index") & filters.user(ADMINS) & filters.private)
async def index_files(bot, message: Message):
    if not message.forward_from_chat:
        return await message.reply_text("कृपया चैनल से एक मैसेज फॉरवर्ड करें।")
    
    channel_id = message.forward_from_chat.id
    msg = await message.reply_text(f"चैनल `({channel_id})` से फाइलों को इंडेक्स करना शुरू किया जा रहा है...")
    
    try:
        total_files = await bot.get_chat_history_count(channel_id)
    except Exception as e:
        return await msg.edit(f"त्रुटि: बॉट शायद इस चैनल का एडमिन नहीं है।\n`{e}`")
        
    await msg.edit(
        f"चैनल में कुल **{total_files}** मैसेज मिले।\nक्या आप इंडेक्सिंग शुरू करना चाहते हैं?",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🚀 इंडेक्सिंग शुरू करें", callback_data=f"start_index_{channel_id}")]]
        )
    )

@Client.on_callback_query(filters.regex(r"^start_index_"))
async def start_indexing_callback(bot, query):
    if query.from_user.id not in ADMINS:
        return await query.answer("यह आपके लिए नहीं है!", show_alert=True)

    channel_id = int(query.data.split("_")[2])
    await query.message.edit(f"`{channel_id}` से फाइलें प्राप्त की जा रही हैं...")
    
    indexing_status[channel_id] = {'received': 0, 'saved': 0, 'duplicate': 0, 'unsupported': 0}
    
    try:
        total = await bot.get_chat_history_count(channel_id)
        async for msg in bot.get_chat_history(channel_id):
            status = indexing_status[channel_id]
            status['received'] += 1
            
            if status['received'] % 200 == 0:
                text = (
                    f"**इंडेक्सिंग प्रगति:**\n\n"
                    f"कुल मैसेज: {total}\n"
                    f"प्राप्त: {status['received']}\n"
                    f"सेव की गईं: {status['saved']}\n"
                    f"डुप्लिकेट: {status['duplicate']}\n"
                    f"असमर्थित: {status['unsupported']}"
                )
                try:
                    await query.message.edit(text)
                except FloodWait as e:
                    await asyncio.sleep(e.x)

            if msg.media:
                media = getattr(msg, msg.media.value, None)
                if media and hasattr(media, 'file_id'):
                    file_id = media.file_id
                    file_name = getattr(media, 'file_name', 'N/A')
                    
                    saved, duplicate = await db.add_file({
                        '_id': file_id, 'file_name': file_name,
                        'caption': msg.caption or "", 'file_size': media.file_size,
                        'chat_id': msg.chat.id, 'message_id': msg.id
                    })
                    if saved: status['saved'] += 1
                    elif duplicate: status['duplicate'] += 1
                else: status['unsupported'] += 1
            else: status['unsupported'] += 1

        status = indexing_status[channel_id]
        await query.message.edit(
            f"**इंडेक्सिंग पूरी हुई!**\n\n"
            f"कुल मैसेज: {total}\n"
            f"सेव की गईं: {status['saved']}\n"
            f"डुप्लिकेट: {status['duplicate']}\n"
            f"असमर्थित: {status['unsupported']}"
        )
    except Exception as e:
        await query.message.edit(f"एक त्रुटि हुई: {e}")
    finally:
        if channel_id in indexing_status: del indexing_status[channel_id]
                
