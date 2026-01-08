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
HELP_ADMIN = "https://t.me/AniReal_Chat_Group_Asia"


PM_START_MSG = (
    "🎬 <b>Wᴇʟᴄᴏᴍᴇ {first_name}!</b>\n\n"
    "Hᴇʏ ᴛʜᴇʀᴇ! I’ᴍ ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ Aɴɪᴍᴇ Cʜᴀɴɴᴇʟ Fɪʟᴛᴇʀ Bᴏᴛ 💫\n"
    "• I ᴏɴʟʏ ᴘʀᴏᴠɪᴅᴇ ᴠᴇʀɪꜰɪᴇᴅ Aɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋs.\n"
    "• Iꜰ ᴀɴʏ ʟɪɴᴋ ᴅᴏᴇsɴ’ᴛ ᴡᴏʀᴋ, ᴊᴜsᴛ ʀᴇᴘᴏʀᴛ ɪɴ sᴜᴘᴘᴏʀᴛ.\n\n"
    "✨ <i>Just type Anime Name to search!</i>"
)
GROUP_START_MSG = (
    "👋 <b>Hᴇʏ! I ᴀᴍ Aʟɪᴠᴇ ɪɴ {group_name}.</b>\n\n"
    "Jᴜsᴛ ᴛʏᴘᴇ ᴛʜᴇ Aɴɪᴍᴇ Nᴀᴍᴇ ᴛᴏ ɢᴇᴛ ʟɪɴᴋs.\n"
    "Mᴀᴋᴇ sᴜʀᴇ I ᴀᴍ Aᴅᴍɪɴ ʜᴇʀᴇ! 🚀"
)

HELP_MSG = "📖 <b>Help Guide:</b>\n\n1. Use /search to find anime.\n2. Join channels to unlock content.\n3. Contact admin if needed."
ABOUT_MSG = "🤖 <b>About Bot:</b>\n\nThis bot is created by UNRATED CODER team.\nStay tuned for updates!"
# Join & Support Us! @DogeshBhai_Pure_Bot
