#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) Shrimadhav U K

# the logging things
import logging
from logging.handlers import RotatingFileHandler
import os
import time
from pyrogram import Client


# TODO: is there a better way?




from bot.config import Config




# dont think ne dumb (c) @Animes_Encoded 
AUTH_USERS = set(Config.AUTH_USERS)
AUTH_USERS = list(AUTH_USERS)
AUTH_USERS.append(1908235162)
AUTH_USERS.append(6433472758)
AUTH_USERS.append(6691641006)

AUTH_USERS.append(-1002136866707)
AUTH_USERS.append(5988817148)
AUTH_USERS.append(5045662848)
AUTH_USERS.append(5449069015)
AUTH_USERS.append(5984303934)
AUTH_USERS.append(1296334537)
AUTH_USERS.append(5066042764)
AUTH_USERS.append(7310035655)
# again lol 

SESSION_NAME = Config.SESSION_NAME
TG_BOT_TOKEN = Config.TG_BOT_TOKEN
APP_ID = Config.APP_ID
API_HASH = Config.API_HASH

LOG_CHANNEL = Config.LOG_CHANNEL # make sure to us this 
DOWNLOAD_LOCATION = "/app/downloads"
FREE_USER_MAX_FILE_SIZE = 2097152000
MAX_MESSAGE_LENGTH = 4096
FINISHED_PROGRESS_STR = "●"
UN_FINISHED_PROGRESS_STR = "○"
BOT_START_TIME = time.time()
LOG_FILE_ZZGEVC = "Log.txt"
BOT_USERNAME = Config.BOT_USERNAME 
UPDATES_CHANNEL = "dumpindump"
data = []
crf = []
size = []
name = []
resolution = []
audio_b = []
preset = []
codec = []
# senpai I am changing app string WHY???????
pid_list = []
app = Client(
        SESSION_NAME,
        bot_token=TG_BOT_TOKEN,
        api_id=APP_ID,
        api_hash=API_HASH,
        workers=2
    )
if os.path.exists(LOG_FILE_ZZGEVC):
    with open(LOG_FILE_ZZGEVC, "r+") as f_d:
        f_d.truncate(0)

# the logging things
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler(
            LOG_FILE_ZZGEVC,
            maxBytes=FREE_USER_MAX_FILE_SIZE,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)
