import requests
import time
from bot_instance import bot
import config

def get_anime_info(name):
    try:
        res = requests.get(f"https://api.jikan.moe/v4/anime?q={name}&limit=1").json()
        if res['data']:
            d = res['data'][0]
            return {
                "title": d['title'],
                "poster": d['images']['jpg']['large_image_url'],
                "details": f"🌟 <b>{d['title']}</b>\n\n⭐ <b>Rating:</b> {d.get('score','N/A')}\n🎭 <b>Genres:</b> {', '.join([g['name'] for g in d['genres']])}\n🔢 <b>Episodes:</b> {d.get('episodes','N/A')}\n\n📝 <b>Synopsis:</b> {d.get('synopsis','')[:200]}..."
            }
    except: return None

def send_log(text):
    try: bot.send_message(config.LOG_CHANNEL_ID, f"📑 <b>SYSTEM LOG:</b>\n{text}")
    except: pass
