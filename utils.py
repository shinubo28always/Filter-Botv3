import requests

def get_anime_info(name):
    try:
        # Jikan API (MAL) for Best Quality Data
        res = requests.get(f"https://api.jikan.moe/v4/anime?q={name}&limit=1").json()
        if res['data']:
            d = res['data'][0]
            
            # Formatting Data
            title = d.get('title', 'N/A')
            episodes = d.get('episodes', 'N/A')
            season = f"{d.get('season', 'N/A')} {d.get('year', '')}".strip()
            genres = ", ".join([g['name'] for g in d.get('genres', [])])
            # Best Quality Image from MAL
            poster = d['images']['jpg']['large_image_url']
            
            # --- AAPKA FONT STYLE ---
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
