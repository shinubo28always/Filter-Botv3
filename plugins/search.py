import time
import config
import database as db
from bot_instance import bot
from telebot import types
from thefuzz import process

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    if message.text.startswith("/"): return
    
    uid = message.from_user.id
    db.add_user(uid)
    
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    
    if not choices: return

    matches = process.extract(query, choices, limit=3)
    best = [m for m in matches if m[1] > 70]
    
    if not best: return

    if best[0][1] >= 95:
        data = db.get_filter(best[0][0])
        send_res(message, data)
    else:
        markup = types.InlineKeyboardMarkup()
        for b in best:
            f_data = db.get_filter(b[0])
            if f_data:
                markup.add(types.InlineKeyboardButton(f_data['title'], callback_data=f"fuz|{b[0]}"))
        bot.reply_to(message, "🧐 <b>Kya aap ye dhund rahe hain?</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz_btn(call):
    key = call.data.split("|")[1]
    data = db.get_filter(key)
    if data:
        send_res(call.message, data, is_cb=True)

def send_res(message, data, is_cb=False):
    target_chat = message.chat.id
    
    # --- 1. GENERATE DYNAMIC INVITE LINK ---
    try:
        source_id = int(data['source_cid'])
        # Link 5 min expiry, 1 use limit
        expire = int(time.time()) + 300
        invite = bot.create_chat_invite_link(
            chat_id=source_id,
            expire_date=expire,
            member_limit=1
        )
        final_link = invite.invite_link
    except Exception as e:
        print(f"Invite Error: {e}")
        final_link = config.LINK_ANIME_CHANNEL # Fallback link

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🎬 Watch / Download", url=final_link)
    )
    
    # --- 2. COPY MESSAGE FROM DB CHANNEL ---
    try:
        bot.copy_message(
            chat_id=target_chat,
            from_chat_id=int(config.DB_CHANNEL_ID),
            message_id=int(data['db_mid']),
            reply_markup=markup,
            message_effect_id=config.EFFECT_PARTY
        )
    except Exception as e:
        print(f"Copy Error: {e}")
        error_msg = "❌ <b>Result Error!</b>\n\nDatabase channel se post delete ho gayi hai ya Bot wahan Admin nahi hai."
        if is_cb: bot.edit_message_text(error_msg, target_chat, message.message_id)
        else: bot.reply_to(message, error_msg)

    if is_cb:
        try: bot.delete_message(target_chat, message.message_id)
        except: pass
