### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

import requests
import config
from bot_instance import bot

def search_anilist(name):
    """Multiple anime results ki list nikalne ke liye"""
    query = '''
    query ($search: String) {
      Page (perPage: 10) {
        media (search: $search, type: ANIME) {
          id
          format
          title {
            english
            romaji
          }
        }
      }
    }
    '''
    variables = {'search': name}
    url = 'https://graphql.anilist.co'
    try:
        response = requests.post(url, json={'query': query, 'variables': variables})
        data = response.json()
        return data['data']['Page']['media']
    except:
        return []

def get_anime_details(anilist_id):
    """ID se specific anime ki full details nikalne ke liye"""
    query = '''
    query ($id: Int) {
      Media (id: $id, type: ANIME) {
        title {
          english
          romaji
        }
        episodes
        season
        seasonYear
        genres
        bannerImage
        coverImage {
          extraLarge
        }
      }
    }
    '''
    variables = {'id': anilist_id}
    url = 'https://graphql.anilist.co'
    try:
        response = requests.post(url, json={'query': query, 'variables': variables})
        d = response.json()['data']['Media']
        
        title = d['title']['english'] or d['title']['romaji'] or "N/A"
        episodes = d.get('episodes') or "N/A"
        season = f"{d.get('season') or 'N/A'} {d.get('seasonYear') or ''}".strip().lower()
        genres = ", ".join(d.get('genres', []))

        # Prefer bannerImage (landscape/wide) over coverImage (portrait)
        poster = d.get('bannerImage') or d['coverImage']['extraLarge']
        
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
    except:
        return None

def send_log(text):
    try: bot.send_message(config.LOG_CHANNEL_ID, f"📑 <b>SYSTEM LOG:</b>\n{text}", parse_mode='HTML')
    except: pass
