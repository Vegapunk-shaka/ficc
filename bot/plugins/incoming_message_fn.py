import datetime
import logging
import os
import time
import asyncio
import json
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import (
    DOWNLOAD_LOCATION, 
    AUTH_USERS,
    LOG_CHANNEL,
    DUMP_CHANNEL,  
    app  
)
from bot.helper_funcs.ffmpeg import convert_video, media_info, take_screen_shot
from bot.helper_funcs.display_progress import progress_for_pyrogram, TimeFormatter

logging.basicConfig(
    level=logging.DEBUG,  # Set to INFO or WARNING to reduce verbosity
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

bot = app        

async def incoming_start_message_f(bot, update):
    await bot.send_message(
        chat_id=update.chat.id,
        text="Bot started!",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Channel', url='tg://settings/Hacked')]]
        ),
        reply_to_message_id=update.id,
    )

async def incoming_compress_message_f(update):
    d_start = time.time()
    sent_message = await bot.send_message(
        chat_id=update.chat.id,
        text="Download started...",
        reply_to_message_id=update.id
    )
    
    try:
        video = await bot.download_media(
            message=update,  
            progress=progress_for_pyrogram,
            progress_args=(bot, "Downloading...", sent_message, d_start)
        )
        if video is None:
            await sent_message.edit_text("Download stopped")
            return

        await sent_message.edit_text("Download complete")
        
        duration, bitrate = await media_info(video)
        if not duration or not bitrate:
            await sent_message.edit_text("Error: Failed to get media info")
            return
        
        await sent_message.edit_text("Compressing video...")
        compressed_video = await convert_video(video, DOWNLOAD_LOCATION, duration, bot, sent_message, None)
        if compressed_video is None:
            await sent_message.edit_text("Compression failed")
            return

        thumb_image_path = await take_screen_shot(compressed_video, os.path.dirname(compressed_video), 5)

        await sent_message.edit_text("Uploading video...")
        await bot.send_video(
            chat_id=update.chat.id,
            video=compressed_video,
            caption="Compressed Video",
            duration=duration,
            thumb="thumb.jpg",
            reply_to_message_id=update.id,
            progress=progress_for_pyrogram,
            progress_args=(bot, "Uploading...", sent_message, time.time())
        )

        await bot.forward_messages(
            chat_id=DUMP_CHANNEL,
            from_chat_id=update.chat.id,
            message_ids=update.id
        )
        await bot.send_message(chat_id=DUMP_CHANNEL, text="Original Video", reply_to_message_id=update.id)
        
    except Exception as e:
        LOGGER.error(f"Error during processing: {e}")
        await sent_message.edit_text(f"Error: {e}")

async def incoming_cancel_message_f(bot, update):
    if update.from_user.id not in AUTH_USERS:      
        await update.message.delete()
        return

    status = os.path.join(DOWNLOAD_LOCATION, "status.json")
    if os.path.exists(status):
        with open(status, 'r') as f:
            statusMsg = json.load(f)
        
        if statusMsg.get('running', False):
            await update.reply_text("Are you sure? This will stop the compression!")
        else:
            await bot.send_message(
                chat_id=update.chat.id,
                text="No active compression exists",
                reply_to_message_id=update.id
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text="No active compression exists",
            reply_to_message_id=update.id
        )
