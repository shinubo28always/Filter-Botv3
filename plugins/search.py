from bot_instance import bot
from telebot import types
import database as db
import config
import time
from thefuzz import process

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    # Skip if it's a command
    if message.text.startswith("/"):
        return

    # Debugging: Render Logs mein dikhega
    print(f"DEBUG: Search received: {message.text}")

    uid = message.from_user.id
    
    # Simple User Add (No await/heavy logic)
    try:
        db.add_user(uid)
    except:
        print("❌ MongoDB User Add Error")

    query = message.text.lower().strip()
    
    # MongoDB Keywords Fetch
    try:
        choices = db.get_all_keywords()
    except Exception as e:
        print(f"❌ MongoDB Fetch Error: {e}")
        return

    if not choices:
        if message.chat.type == "private":
            bot.reply_to(message, "📂 Database abhi khali hai.")
        return

    # Match dhundna
    matches = process.extract(query, choices, limit=3)
    best = [m for m in matches if m[1] > 70]

    if not best:
        if message.chat.type == "private":
            bot.reply_to(message, "❌ Kuch nahi mila.")
        return

    # Sahi match milne par
    data = db.get_filter(best[0][0])
    if not data: return

    # Temporary Link
    try:
        expire = int(time.time()) + 300
        invite = bot.create_chat_invite_link(data['source_cid'], expire_date=expire, member_limit=1)
        link = invite.invite_link
    except:
        link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch Now", url=link))

    try:
        bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=config.DB_CHANNEL_ID,
            message_id=data['db_mid'],
            reply_markup=markup,
            message_effect_id=config.EFFECT_PARTY
        )
    except Exception as e:
        print(f"❌ Copy Message Error: {e}")
        bot.reply_to(message, "❌ Link invalid ya DB se deleted hai.")
