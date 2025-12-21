import os
from dotenv import load_dotenv

# .env file load karna (Sirf local testing ke liye kaam aayegi)
load_dotenv()

def get_config(key, default=None):
    """
    Priority Logic:
    1. Hardcoded Value in this file (if not empty)
    2. .env file
    3. Host Service Variables (System Env)
    """
    # 1. Yahan Hardcode karein (Highest Priority)
    hardcoded = {
        "API_TOKEN": "",  # Agar yahan token dala toh wahi chalega
        "OWNER_ID": "",   # Eg: "7009167334"
        "MONGO_URI": "",
        "DB_CHANNEL_ID": "",
        "LOG_CHANNEL_ID": ""
    }

    # Check if hardcoded value exists
    if hardcoded.get(key):
        return hardcoded[key]
    
    # 2 & 3. Fallback to .env or System Environment Variables
    return os.getenv(key, default)

# --- CONFIGURATION VALUES ---
API_TOKEN = get_config("API_TOKEN")
OWNER_ID = int(get_config("OWNER_ID")) if get_config("OWNER_ID") else 0
MONGO_URI = get_config("MONGO_URI")
DB_CHANNEL_ID = int(get_config("DB_CHANNEL_ID")) if get_config("DB_CHANNEL_ID") else 0
LOG_CHANNEL_ID = int(get_config("LOG_CHANNEL_ID")) if get_config("LOG_CHANNEL_ID") else 0

# Assets
STICKER_ID = "CAACAgUAAxkBAAEP4flpKC6Ozwtd25givMwrN3zMcnLeFQACuBYAArKmaFa__rW3azdtFjYE"
EFFECT_FIRE = "5104841245755180586"
EFFECT_PARTY = "5046509860389126442"

LINK_ANIME_CHANNEL = "https://t.me/Anime_Dekhbo_Official"
LINK_SUPPORT = "https://t.me/DogeshBhai_Pure_Bot"
LINK_REPORT = "https://t.me/+JClk-WQJaMk0NWI1"
