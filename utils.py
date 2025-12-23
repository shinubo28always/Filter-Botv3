import requests
import config
from bot_instance import bot

def get_anime_info(name):
    """MAL se anime details aur HD posters fetch karne ke liye (English Priority)"""
    try:
        # Jikan API Call
        res = requests.get(f"https://api.jikan.moe/v4/anime?q={name}&limit=1").json()
        if res['data']:
            d = res['data'][0]
            
            # --- ENGLISH TITLE LOGIC ---
            # Pehle Official English title dekhega, agar nahi mila toh default title
            title = d.get('title_english') or d.get('title', 'N/A')
            
            episodes = d.get('episodes', 'N/A')
            season = f"{d.get('season', 'N/A')} {d.get('year', '')}".strip()
            genres = ", ".join([g['name'] for g in d.get('genres', [])])
            
            # Best available quality JPG image
            poster = d['images']['jpg']['large_image_url']
            
            # Aapka Stylish Caption Style
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
    except Exception as e:
        print(f"MAL Error: {e}")
        return None

def send_log(text):
    """Log channel mein reports bhejne ke liye"""
    try:
        bot.send_message(config.LOG_CHANNEL_ID, f"📑 <b>SYSTEM LOG:</b>\n{text}", parse_mode='HTML')
    except Exception as e:
        print(f"Log Error: {e}")
