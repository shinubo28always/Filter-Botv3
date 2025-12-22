import time
import config
import database as db
from bot_instance import bot
from telebot import types
from thefuzz import process
from utils import send_log

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
        send_final_result(message, data)
    else:
        markup = types.InlineKeyboardMarkup()
        for b in best:
            f_data = db.get_filter(b[0])
            if f_data:
                markup.add(types.InlineKeyboardButton(f_data['title'], callback_data=f"fuz|{b[0]}"))
        bot.reply_to(message, "🧐 <b>Did you mean:</b>", reply_markup=markup)

def send_final_result(message, data, is_cb=False):
    target = message.chat.id
    
    # 1. GENERATE TEMPORARY INVITE LINK (5 Min Expiry)
    try:
        expire_time = int(time.time()) + 300
        invite = bot.create_chat_invite_link(
            chat_id=int(data['source_cid']), 
            expire_date=expire_time, 
            member_limit=1
        )
        temp_link = invite.invite_link
    except Exception as e:
        send_log(f"❌ Invite Link Error: {e}\nCID: {data['source_cid']}")
        temp_link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=temp_link))
    
    # 2. COPY MESSAGE FROM DB CHANNEL
    try:
        # NOTE: Humne 'message_effect_id' hata diya hai kyunki copy_message ise support nahi karta
        bot.copy_message(
            chat_id=target,
            from_chat_id=int(config.DB_CHANNEL_ID),
            message_id=int(data['db_mid']),
            reply_markup=markup
        )
    except Exception as e:
        send_log(f"❌ Copy Message Error: {e}\nFrom: {config.DB_CHANNEL_ID}\nMID: {data['db_mid']}")
        # Agar error aaye toh user ko clear message dikhayein
        if is_cb:
            bot.edit_message_text("❌ <b>Result Error!</b>\nPost DB se delete ho chuki hai.", target, message.message_id)
        else:
            bot.reply_to(message, "❌ <b>Result Error!</b>\nAdmin ko report karein ya permissions check karein.")

    if is_cb:
        try: bot.delete_message(target, message.message_id)
        except: pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuzzy(call):
    key = call.data.split("|")[1]
    data = db.get_filter(key)
    if data: send_final_result(call.message, data, is_cb=True)
