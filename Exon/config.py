"""
MIT License

Copyright (c) 2022 ABISHNOI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# ""DEAR PRO PEOPLE,  DON'T REMOVE & CHANGE THIS LINE
# TG :- @Abishnoi
#     MY ALL BOTS :- Abishnoi_bots
#     GITHUB :- KingAbishnoi ""


import json
import os


def get_user_list(config, key):
    with open("{}/Exon/{}".format(os.getcwd(), config), "r") as json_file:
        return json.load(json_file)[key]


# Create a new config.py or rename this to config.py file in same dir and import, then extend this class.
class Config(object):
    LOGGER = True
    # REQUIRED
    # Login to https://my.telegram.org and fill in these slots with the details given by it

    TOKEN = "TOKEN" 
    OWNER_ID = "OWNER_ID" 
    JOIN_LOGGER = "" 
    OWNER_USERNAME = "" 
    ALLOW_CHATS = "" 
    DRAGONS = "" 
    DEV_USERS = "" 
    DEMONS = "" 
    WOLVES = "" 
    TIGERS = "" 
    INFOPIC = "INFOPIC" 
    EVENT_LOGS = "" 
    ERROR_LOGS = "" 
    WEBHOOK = "" 
    URL = "" 
    PORT = "" 
    CERT_PATH = "" 
    API_ID = "API_ID"
    API_HASH = ".API_HASH"
    ARQ_API_URL = "ARQ_API_URL"
    ARQ_API_KEY = "ARQ_API_KEY"
    DB_URL = "DB_URL" 
    DB_URL2 = "DB_URL2"
    DONATION_LINK = "DONATION_LINK" 
    STRICT_GBAN = ".STRICT_GBAN"
    WORKERS = ".WORKERS"
    BAN_STICKER = "BAN_STICKER"
    TEMP_DOWNLOAD_DIRECTORY = "TEMP_DOWNLOAD_DIRECTORY"
    LOAD = ".LOAD"
    NO_LOAD = "NO_LOAD"
    # CASH_API_KEY = Config.CASH_API_KEY
    TIME_API_KEY = "TIME_API_KEY"
    WALL_API = ".WALL_API"
    MONGO_DB_URL = "MONGO_DB_URL"
    MONGO_DB = ".MONGO_DB"
    REDIS_URL = "REDIS_URL"
    SUPPORT_CHAT = "SUPPORT_CHAT"
    UPDATES_CHANNEL = "UPDATES_CHANNEL"
    SPAMWATCH_SUPPORT_CHAT = "SPAMWATCH_SUPPORT_CHAT"
    SPAMWATCH_API = ".SPAMWATCH_API"
    REM_BG_API_KEY = "REM_BG_API_KEY"
    OPENWEATHERMAP_ID = "OPENWEATHERMAP_ID"
    APP_ID = ".APP_ID"
    APP_HASH = "APP_HASH"
    GENIUS_API_TOKEN = "GENIUS_API_TOKEN"
    # YOUTUBE_API_KEY = Config.YOUTUBE_API_KEY
    HELP_IMG = ".HELP_IMG"
    START_IMG = "" 
    


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True


#NO NEED EDIT 


