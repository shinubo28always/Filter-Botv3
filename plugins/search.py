import config
import database as db
from bot_instance import bot
from telebot import types
from thefuzz import process

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    if message.text.startswith("/"): return
    
    uid = message.from_user.id
    db.add_user(uid) # Save user for broadcast
    
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices: return

    matches = process.extract(query, choices, limit=5)
    best = [m for m in matches if m[1] > 70]
    if not best: return

    # Direct Match
    if best[0][1] >= 95:
        data = db.get_filter(best[0][0])
        send_res(message, data, message.message_id)
        return

    # Suggestion with User Lock
    markup = types.InlineKeyboardMarkup()
    for b in best:
        f_data = db.get_filter(b[0])
        if f_data:
            cb = f"fuz|{b[0][:20]}|{message.message_id}|{uid}"
            markup.add(types.InlineKeyboardButton(f"🎬 {f_data['title']}", callback_data=cb))
    
    bot.reply_to(message, f"🧐 <b>Hey {message.from_user.first_name}, did you mean:</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz(call):
    _, key, mid, original_uid = call.data.split("|")
    if int(call.from_user.id) != int(original_uid) and not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "⚠️ Ye aapka request nahi hai!", show_alert=True)

    data = db.get_filter(key)
    if data:
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        send_res(call.message, data, int(mid))

def send_res(message, data, reply_mid):
    # PERMANENT LINK (No Expiry)
    try:
        # Link ko permanent banane ke liye expire_date hata diya
        invite = bot.create_chat_invite_link(int(data['source_cid']), member_limit=0)
        link = invite.invite_link
    except:
        link = "https://t.me/DogeshBhai_Pure_Bot"

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    
    try:
        bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=config.DB_CHANNEL_ID,
            message_id=int(data['db_mid']),
            reply_markup=markup,
            reply_to_message_id=reply_mid
        )
    except:
        bot.send_message(message.chat.id, "❌ Post not found in DB Channel.", reply_to_message_id=reply_mid)
