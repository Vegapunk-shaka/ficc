import logging
import asyncio
import os
import time
import shlex
import re
import json
import subprocess
import math
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.helper_funcs.display_progress import TimeFormatter
from bot.localisation import Localisation
from bot import FINISHED_PROGRESS_STR, UN_FINISHED_PROGRESS_STR, DOWNLOAD_LOCATION, crf, resolution, audio_b, preset, codec, name, size, pid_list

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)

async def convert_video(video_file, output_directory, total_time, bot, message, chan_msg):
    out_put_file_name = os.path.join(output_directory, video_file + ".mkv")
    progress = os.path.join(output_directory, "progress.txt")
    with open(progress, 'w') as f:
        pass

    # Setting defaults if not already set
    crf.append("28")
    codec.append("libx265")
    resolution.append("1280x720")
    preset.append("ultrafast")
    audio_b.append("40k")
    name.append("Owner of this video is free edu care")
    size.append("18")

    file_genertor_command = (
    f"ffmpeg -hide_banner -loglevel quiet -progress {shlex.quote(progress)} "
    f"-i {shlex.quote(video_file)} "
    f"-metadata title='Encoded by @zoro_is_robot' -c:v libx265 -map 0 -crf {crf[0]} -c:s copy -pix_fmt yuv420p "
    f"-b:v 1000k -c:a libopus -b:a {audio_b[0]} -preset {preset[0]} "
    f"-metadata:s:v title='@zoro_is_robot' -metadata:s:a title='@zoro_is_robot' -metadata:s:s title='@zoro_is_robot' "
    f"-vf \"drawtext=fontfile=font.ttf:fontsize={size[0]}:fontcolor=white:bordercolor=black@0.50:"
    f"x=w-tw-10:y=10:box=1:boxcolor=black@0.5:boxborderw=4:text='{name[0]}'\" "
    f"{shlex.quote(out_put_file_name)} -y"
)



    COMPRESSION_START_TIME = time.time()
    process = await asyncio.create_subprocess_shell(
        file_genertor_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    LOGGER.info("ffmpeg_process: " + str(process.pid))
    pid_list.insert(0, process.pid)
    status = os.path.join(output_directory, "status.json")
    with open(status, 'r+') as f:
        statusMsg = json.load(f)
        statusMsg['pid'] = process.pid
        statusMsg['message'] = message.id
        f.seek(0)
        json.dump(statusMsg, f, indent=2)

    isDone = False
    while process.returncode is None:
        await asyncio.sleep(3)
        with open(progress, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()
            frame = re.findall("frame=(\d+)", text)
            time_in_us = re.findall("out_time_ms=(\d+)", text)
            progress_matches = re.findall("progress=(\w+)", text)
            speed = re.findall("speed=(\d+\.?\d*)", text)
            if len(frame):
                frame = int(frame[-1])
            else:
                frame = 1
            if len(speed):
                speed = speed[-1]
            else:
                speed = 1
            if len(time_in_us):
                time_in_us = time_in_us[-1]
            else:
                time_in_us = 1
            if len(progress_matches):
                if progress_matches[-1] == "end":
                    LOGGER.info(progress_matches[-1])
                    isDone = True
                    break
            execution_time = TimeFormatter((time.time() - COMPRESSION_START_TIME) * 1000)
            elapsed_time = int(time_in_us) / 1000000
            difference = math.floor((total_time - elapsed_time) / float(speed))
            ETA = "-"
            if difference > 0:
                ETA = TimeFormatter(difference * 1000)
            percentage = math.floor(elapsed_time * 100 / total_time)
            progress_str = "<blockquote><b>ᴘʀᴏɢʀᴇss:</b> {0}%\n[{1}{2}]</blockquote>".format(
                round(percentage, 2),
                ''.join([FINISHED_PROGRESS_STR for _ in range(math.floor(percentage / 10))]),
                ''.join([UN_FINISHED_PROGRESS_STR for _ in range(10 - math.floor(percentage / 10))])
            )
            stats = f'<blockquote> <b>ᴇɴᴄᴏᴅɪɴɢ ɪɴ ᴘʀᴏɢʀᴇss</b></blockquote>\n' \
                    f'<blockquote><b>ᴛɪᴍᴇ ʟᴇғᴛ:</b> {ETA}</blockquote>\n' \
                    f'{progress_str}\n'
            try:
                await message.edit_text(
                    text=stats,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton('❌ Cancel ❌', callback_data='fuckingdo')]
                        ]
                    )
                )
            except Exception as e:
                LOGGER.error(f"Failed to edit message: {e}")

            if chan_msg is not None:
                try:
                    await chan_msg.edit_text(text=stats)
                except Exception as e:
                    LOGGER.error(f"Failed to edit chan_msg: {e}")
            else:
                LOGGER.warning("chan_msg is None, skipping chan_msg.edit_text.")

    stdout, stderr = await process.communicate()
    e_response = stderr.decode('utf-8', errors='ignore').strip()
    t_response = stdout.decode('utf-8', errors='ignore').strip()
    LOGGER.info(e_response)
    LOGGER.info(t_response)
    del pid_list[0]
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None

async def media_info(saved_file_path):
    process = subprocess.Popen(
        ['ffmpeg', "-hide_banner", '-i', saved_file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout, stderr = process.communicate()
    output = stdout.decode('utf-8', errors='ignore').strip()
    duration = re.search("Duration:\\s*(\\d*):(\\d*):(\\d+\\.?\\d*)[\\s\\w*$]", output)
    bitrates = re.search("bitrate:\\s*(\\d+)[\\s\\w*$]", output)

    if duration is not None:
        hours = int(duration.group(1))
        minutes = int(duration.group(2))
        seconds = math.floor(float(duration.group(3)))
        total_seconds = (hours * 60 * 60) + (minutes * 60) + seconds
    else:
        total_seconds = None
    if bitrates is not None:
        bitrate = bitrates.group(1)
    else:
        bitrate = None
    return total_seconds, bitrate

async def take_screen_shot(video_file, output_directory, ttl):
    out_put_file_name = os.path.join(output_directory, str(time.time()) + ".jpg")
    if video_file.upper().endswith(("MKV", "MP4", "WEBM")):
        file_genertor_command = [
            "ffmpeg",
            "-ss",
            str(ttl),
            "-i",
            video_file,
            "-vframes",
            "1",
            out_put_file_name
        ]

        process = await asyncio.create_subprocess_exec(
            *file_genertor_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        e_response = stderr.decode('utf-8', errors='ignore').strip()
        t_response = stdout.decode('utf-8', errors='ignore').strip()

    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None

def get_width_height(video_file):
    metadata = extractMetadata(createParser(video_file))
    if metadata.has("width") and metadata.has("height"):
        return metadata.get("width"), metadata.get("height")
    else:
        return 1280, 720
