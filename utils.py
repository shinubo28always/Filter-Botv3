import requests
import config
from bot_instance import bot

def get_anime_info(name):
    try:
        res = requests.get(f"https://api.jikan.moe/v4/anime?q={name}&limit=1").json()
        if res['data']:
            d = res['data'][0]
            title = d.get('title', 'N/A')
            episodes = d.get('episodes', 'N/A')
            season = f"{d.get('season', 'N/A')} {d.get('year', '')}".strip()
            genres = ", ".join([g['name'] for g in d.get('genres', [])])
            poster = d['images']['jpg']['large_image_url']
            
            caption = (
                f"<b>🔰 {title} </b>\n"
                f"<blockquote><b>━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"‣ Episodes: {episodes}\n"
                f"‣ Season: {season}\n"
                f"‣ Quality: Multiple\n"
                f"‣ Audio: हिंदी (Hindi) #Official\n"
                f"‣ Genres: {genres}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━</b></blockquote>"
            )
            return {"title": title, "poster": poster, "caption": caption}
    except: return None

def send_log(text):
    try: bot.send_message(config.LOG_CHANNEL_ID, f"📑 <b>SYSTEM LOG:</b>\n{text}")
    except: pass
