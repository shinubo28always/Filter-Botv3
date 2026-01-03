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

LINK_ANIME_CHANNEL = "https://t.me/DogeshBhai_Pure_Bot"
HELP_ADMIN = "https://AniReal_Chat_Group_Asia"

# Join & Support Us! @DogeshBhai_Pure_Bot
