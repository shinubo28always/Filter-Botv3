# Please Support Us! @DogeshBhai_Pure_Bot on Telegram! 
# This Bot Created By: @AniReal_Support!
import os
from dotenv import load_dotenv

load_dotenv()

def get_config(key, default=None):
    # Priority: 1. Hardcoded, 2. .env, 3. Host Env
    hardcoded = {
        "API_TOKEN": "", 
        "OWNER_ID": "", 
        "MONGO_URI": "",
        "DB_CHANNEL_ID": "",
        "LOG_CHANNEL_ID": ""
    }
    val = hardcoded.get(key) or os.getenv(key)
    return val if val else default

API_TOKEN = get_config("API_TOKEN")
OWNER_ID = int(get_config("OWNER_ID")) if get_config("OWNER_ID") else 0
MONGO_URI = get_config("MONGO_URI")
DB_CHANNEL_ID = int(get_config("DB_CHANNEL_ID")) if get_config("DB_CHANNEL_ID") else 0
LOG_CHANNEL_ID = int(get_config("LOG_CHANNEL_ID")) if get_config("LOG_CHANNEL_ID") else 0

# Static Assets
STICKER_ID = "CAACAgUAAxkBAAEP4flpKC6Ozwtd25givMwrN3zMcnLeFQACuBYAArKmaFa__rW3azdtFjYE"
EFFECT_FIRE = "5104841245755180586"
EFFECT_PARTY = "5046509860389126442"
START_IMG = "https://graph.org/file/fdc4357abfaba23255e98-24d1bbfa3888cdfcfe.jpg"

LINK_ANIME_CHANNEL = "https://t.me/UNRATED_CODER"
HELP_ADMIN = "https://t.me/AniReal_Chat_Group_Asia"


PM_START_MSG = (
    "👋 <b>Welcome {first_name}</b>\n\n"
    "<blockquote><b>Send any anime name"
    "I’ll give you verified Telegram channel links." 
    "If any link doesn’t work, report it in Support."
    "Type an anime name to start.</b></blockquote>"
)
GROUP_START_MSG = (
    "👋 <b>Hello {group_name}</b>\n\n"
    "<blockquote><b>"
    "This bot supports <u>Index Finding</u>.\n"
    "If you type only one word, search will be bypassed and index results will be shown.\n\n"
    "You can search any anime by sending its name.\n"
    "If an anime is not available, you can request it using the /request command.\n\n"
    "Make sure I have Admin permission to work properly."
    "</b></blockquote>"
)

HELP_MSG = "<b>How It Works</b>\n\n<blockquote><b>Simply type any anime name (for example:</b> <i>Naruto</i>) <b>and the bot will provide a verified channel link where the anime is available.\n\n🚀 Smart Feature:\nIf the anime you are looking for is not available, you can use the /request command to submit a request for future uploads.</b></blockquote>\n\n<b>Developed by:</b> <i>@UNRATED_CODER</i>"
ABOUT_MSG = "<b>About This Bot</b>\n\n<blockquote><b>This bot is fast, secure, and reliable, providing access only to official and verified Telegram channels. There is no risk of device hacking or any unauthorized activity.</b>\n\n<b>The system is optimized for speed and privacy, ensuring a smooth and safe experience for every user.</b>\n<b>For quick access, you can request an index by sending a single word (for example:</b> <i>A</i>) <b>and receive the related index instantly.</b></blockquote>\n\n<b>Developed By:</b> <i>@UNRATED_CODER</i>"
# Join & Support Us! @DogeshBhai_Pure_Bot
