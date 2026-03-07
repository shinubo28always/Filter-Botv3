# Please Support Us! @UNRATED_CODER on Telegram! 
# This Bot Created By: @UNRATED_CODER!
import os
from dotenv import load_dotenv

load_dotenv()

def get_config(key, default=None, required=False):
    # Priority: 1. Hardcoded, 2. .env, 3. Host Env
    hardcoded = {
        "API_TOKEN": "", 
        "OWNER_ID": "", 
        "MONGO_URI": "",
        "DB_CHANNEL_ID": "",
        "LOG_CHANNEL_ID": ""
    }
    val = hardcoded.get(key) or os.getenv(key)
    if required and not val:
        raise ValueError(f"CRITICAL ERROR: Configuration '{key}' is missing! Please set it in .env or hardcode it.")
    return val if val else default

# Mandatory Configs
API_TOKEN = get_config("API_TOKEN", required=True)
OWNER_ID = int(get_config("OWNER_ID", required=True))
MONGO_URI = get_config("MONGO_URI", required=True)
DB_CHANNEL_ID = int(get_config("DB_CHANNEL_ID", required=True))
LOG_CHANNEL_ID = int(get_config("LOG_CHANNEL_ID", required=True))

# Static Assets
STICKER_ID = "CAACAgUAAxkBAAEP4flpKC6Ozwtd25givMwrN3zMcnLeFQACuBYAArKmaFa__rW3azdtFjYE"
EFFECT_FIRE = "5104841245755180586"
EFFECT_PARTY = "5046509860389126442"
START_IMG = "https://graph.org/file/fdc4357abfaba23255e98-24d1bbfa3888cdfcfe.jpg"

LINK_ANIME_CHANNEL = "https://t.me/UNRATED_CODER"
HELP_ADMIN = "https://t.me/AniReal_Chat_Group_Asia"


PM_START_MSG = (
    "👋 <b>Wᴇʟᴄᴏᴍᴇ {first_name}!</b>\n\n"
    "<blockquote><b>"
    "Hᴇʏ ᴛʜᴇʀᴇ! I’ᴍ ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ Aɴɪᴍᴇ Cʜᴀɴɴᴇʟ Fɪʟᴛᴇʀ Bᴏᴛ 💫\n\n"
    "• I ᴏɴʟʏ ᴘʀᴏᴠɪᴅᴇ ᴠᴇʀɪꜰɪᴇᴅ Aɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋs.\n"
    "• Iꜰ ᴀɴʏ ʟɪɴᴋ ᴅᴏᴇsɴ’ᴛ ᴡᴏʀᴋ, ᴊᴜsᴛ ʀᴇᴘᴏʀᴛ ɪɴ sᴜᴘᴘᴏʀᴛ.\n\n"
    "✨ <i>Just type an Anime Name to search!</i>"
    "</b></blockquote>\n"
    "<b>Support chat - @Secret_Chat_Pro_Robot</b>"
)

GROUP_START_MSG = (
    "<b>👋 ʜᴇʏ ɪ'ᴍ ᴀʟɪᴠᴇ! 🫠.\n"
    "Jᴜsᴛ ᴛʏᴘᴇ <a href='https://t.me/AniFlow_Animes'>Anime Name</a> ᴛᴏ sᴇᴀʀᴄʜ.</b>"
)

GROUP_AUTH_MSG = (
    "👋 <b>Hᴇʏ! I ᴀᴍ Aʟɪᴠᴇ in {group_name}.</b>\n\n"
    "<blockquote><b>"
    "• Just type any Anime Name to search verified channels.\n"
    "• If a link doesn’t work, report it in Support.\n"
    "• If an anime is missing, request it using /request.\n\n"
    "Make sure I have Admin permission for full functionality 🚀"
    "</b></blockquote>"
)

HELP_MSG = "<blockquote><b>Simply type any anime name (for example:</b> <i>Naruto</i>) <b>and the bot will provide a verified channel link where the anime is available.\n\n🚀 Smart Feature:\nIf the anime you are looking for is not available, you can use the /request command to submit a request for future uploads.</b></blockquote>\n<b>Developed by:</b> <i>@UNRATED_CODER</i>"
ABOUT_MSG = "<blockquote><b>This bot is fast, secure, and reliable, providing access only to official and verified Telegram channels. There is no risk of device hacking or any unauthorized activity.</b>\n\n<b>The system is optimized for speed and privacy, ensuring a smooth and safe experience for every user.</b>\n<b>For quick access, you can request an index by sending a single word (for example:</b> <i>A</i>) <b>and receive the related index instantly.</b></blockquote>\n<b>Developed By:</b> <i>@UNRATED_CODER</i>"
# Join & Support Us! @UNRATED_CODER
