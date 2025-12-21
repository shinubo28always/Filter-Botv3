import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
MONGO_URI = os.getenv("MONGO_URI")
DB_CHANNEL_ID = int(os.getenv("DB_CHANNEL_ID"))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

# Assets & Links
STICKER_ID = "CAACAgUAAxkBAAEP4flpKC6Ozwtd25givMwrN3zMcnLeFQACuBYAArKmaFa__rW3azdtFjYE"
EFFECT_FIRE = "5104841245755180586"
EFFECT_PARTY = "5046509860389126442"

LINK_ANIME_CHANNEL = "https://t.me/Anime_Dekhbo_Official"
LINK_SUPPORT = "https://t.me/DogeshBhai_Pure_Bot"
LINK_REPORT = "https://t.me/+JClk-WQJaMk0NWI1"
