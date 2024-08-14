import datetime
import logging
import os
import time
import asyncio
import json
from PIL import Image  # Ensure Pillow is installed: pip install pillow
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.localisation import Localisation
from bot import (
    DOWNLOAD_LOCATION, 
    AUTH_USERS,
    LOG_CHANNEL,
    app  
)
from bot.helper_funcs.ffmpeg import (
    convert_video,
    media_info,
    take_screen_shot
)
from bot.helper_funcs.display_progress import (
    progress_for_pyrogram,
    TimeFormatter,
    humanbytes
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

CURRENT_PROCESSES = {}
CHAT_FLOOD = {}
broadcast_ids = {}
bot = app  
DUMP_CHANNEL = "YOUR_DUMP_CHANNEL_ID"  # Replace with your dump channel ID

async def incoming_start_message_f(bot, update):
    await bot.send_message(
        chat_id=update.chat.id,
        text=Localisation.START_TEXT,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('Channel', url='tg://settings/Hacked')
                ]
            ]
        ),
        reply_to_message_id=update.id,
    )

os.system("wget https://graph.org/file/fb8fec6399fcc10a8df9f.jpg -O thumb.jpg")
    
async def incoming_compress_message_f(update):
    isAuto = True
    d_start = time.time()
    sent_message = await bot.send_message(
        chat_id=update.chat.id,
        text=Localisation.DOWNLOAD_START,
        reply_to_message_id=update.id
    )
    chat_id = LOG_CHANNEL
    utc_now = datetime.datetime.utcnow()
    ist_now = utc_now + datetime.timedelta(minutes=30, hours=5)
    ist = ist_now.strftime("%d/%m/%Y, %H:%M:%S")
    bst_now = utc_now + datetime.timedelta(minutes=00, hours=6)
    bst = bst_now.strftime("%d/%m/%Y, %H:%M:%S")
    now = f"\n{ist} (GMT+05:30)`\n`{bst} (GMT+06:00)"
    download_start = await bot.send_message(chat_id, f"**Bot Become Busy Now !!** \n\nDownload Started at `{now}`")
    
    try:
        d_start = time.time()
        status = DOWNLOAD_LOCATION + "/status.json"
        with open(status, 'w') as f:
            statusMsg = {
                'running': True,
                'message': sent_message.id
            }
            json.dump(statusMsg, f, indent=2)
        video = await bot.download_media(
            message=update,  
            progress=progress_for_pyrogram,
            progress_args=(
                bot,
                Localisation.DOWNLOAD_START,
                sent_message,
                d_start
            )
        )
        saved_file_path = video
        LOGGER.info(saved_file_path)  
        LOGGER.info(video)
        if video is None:
            try:
                await sent_message.edit_text(
                    text="Download stopped"
                )
                await bot.send_message(chat_id, f"**Download Stopped, Bot is Free Now !!** \n\nProcess Done at `{now}`")
                await download_start.delete()
            except:
                pass
            return
    except (ValueError) as e:
        try:
            await sent_message.edit_text(
                text=str(e)
            )
        except:
            pass

    try:
        await sent_message.edit_text(                
            text=Localisation.SAVED_RECVD_DOC_FILE                
        )
    except:
        pass

    if os.path.exists(saved_file_path):
        downloaded_time = TimeFormatter((time.time() - d_start)*1000)
        duration, bitrate = await media_info(saved_file_path)
        if duration is None or bitrate is None:
            try:
                await sent_message.edit_text(                
                    text="<blockquote>⚠️ Getting video meta data failed ⚠️</blockquote>"                
                )
                await bot.send_message(chat_id, f"**Download Failed, Bot is Free Now !!** \n\nProcess Done at `{now}`")
                await download_start.delete()
            except:
                pass
            return

        compress_start = await bot.send_message(chat_id, f"**Compressing Video ...** \n\nProcess Started at `{now}`")
        await sent_message.edit_text(                    
            text=Localisation.COMPRESS_START                    
        )
        c_start = time.time()
        o = await convert_video(
               video, 
               DOWNLOAD_LOCATION, 
               duration, 
               bot, 
               sent_message, 
               compress_start
             )
        compressed_time = TimeFormatter((time.time() - c_start)*1000)
        LOGGER.info(o)
        if o == 'stopped':
            return
        if o is not None:
            await compress_start.delete()

            # Generate thumbnail of the converted video at 5 seconds
            thumb_image_path = await take_screen_shot(
                o,  # Path to the converted video
                os.path.dirname(os.path.abspath(o)),
                5  # Capture at 5 seconds
            )

            upload_start = await bot.send_message(chat_id, f"**Uploading Video ...** \n\nProcess Started at `{now}`")
            await sent_message.edit_text(                    
                text=Localisation.UPLOAD_START,                    
            )
            u_start = time.time()
            
            # Extract the file name without extension
            file_name = os.path.basename(o)  # Gets the full file name
            file_name_without_extension = os.path.splitext(file_name)[0]  # Removes the file extension
            
            upload = await bot.send_video(
                chat_id=update.chat.id,
                video=o,
                caption=file_name_without_extension,  # Use the file name as the caption
                duration=duration,
                thumb="thumb.jpg",  # Use the downloaded thumb image
                width=1280,  # Set the width of the video
                height=720,  # Set the height of the video
                reply_to_message_id=update.id,
                progress=progress_for_pyrogram,
                progress_args=(
                    bot,
                    Localisation.UPLOAD_START,
                    sent_message,
                    u_start
                )
            )
            
            if upload is None:
                try:
                    await sent_message.edit_text(
                        text="Upload stopped"
                    )
                    await bot.send_message(chat_id, f"**Upload Stopped, Bot is Free Now !!** \n\nProcess Done at `{now}`")
                    await upload_start.delete()
                except:
                    pass
                return
            
            uploaded_time = TimeFormatter((time.time() - u_start)*1000)
            await sent_message.delete()
            await upload_start.delete()
            await bot.send_message(chat_id, f"**Upload Done, Bot is Free Now !!** \n\nProcess Done at `{now}`")
            try:
                await upload.edit_caption(
                    caption=file_name_without_extension  # Keep the file name as the caption
                )
            except:
                pass

            # Forward both original and converted files to the dump channel
            await bot.forward_messages(DUMP_CHANNEL, update.chat.id, update.id)  # Forward original video
            await bot.forward_messages(DUMP_CHANNEL, upload.chat.id, upload.id)  # Forward compressed video
        else:
            try:
                await sent_message.edit_text(                    
                    text="<blockquote>⚠️ Compression failed ⚠️</blockquote>"               
                )
                await bot.send_message(chat_id, f"<blockquote>**Compression Failed, Bot is Free Now !!** \n\nProcess Done at `{now}`</blockquote>")
                await download_start.delete()
            except:
                pass
    else:
        try:
            await sent_message.edit_text(                    
                text="<blockquote>⚠️ Failed Downloaded path not exist ⚠️</blockquote>"               
            )
            await bot.send_message(chat_id, f"<blockquote>**Download Error, Bot is Free Now !!** \n\nProcess Done at `{now}`</blockquote>")
            await download_start.delete()
        except:
            pass
    
async def incoming_cancel_message_f(bot, update):
    if update.from_user.id not in AUTH_USERS:      
        try:
            await update.message.delete()
        except:
            pass
        return

    status = DOWNLOAD_LOCATION + "/status.json"
    if os.path.exists(status):
        # Read the status to check if there's an ongoing process
        with open(status, 'r') as f:
            statusMsg = json.load(f)
        
        if statusMsg.get('running', False):
            inline_keyboard = []
            ikeyboard = []
            ikeyboard.append(InlineKeyboardButton("Yes 🚫", callback_data=("fuckingdo").encode("UTF-8")))
            ikeyboard.append(InlineKeyboardButton("No 🤗", callback_data=("fuckoff").encode("UTF-8")))
            inline_keyboard.append(ikeyboard)
            reply_markup = InlineKeyboardMarkup(inline_keyboard)
            await update.reply_text("Are you sure? 🚫 This will stop the compression!", reply_markup=reply_markup, quote=True)
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
