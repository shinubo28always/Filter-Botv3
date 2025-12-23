import time, config, database as db
from bot_instance import bot
from telebot import types
from thefuzz import process

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search(message):
    if message.text.startswith("/"): return
    uid = message.from_user.id
    db.add_user(uid)
    
    choices = db.get_all_keywords()
    if not choices: return
    
    matches = process.extract(message.text.lower(), choices, limit=5)
    best = [m for m in matches if m[1] > 70]
    if not best: return

    if best[0][1] >= 95:
        send_res(message, db.get_filter(best[0][0]), message.message_id)
    else:
        markup = types.InlineKeyboardMarkup()
        for b in best:
            markup.add(types.InlineKeyboardButton(db.get_filter(b[0])['title'], callback_data=f"fuz|{b[0][:20]}|{message.message_id}|{uid}"))
        bot.reply_to(message, "🧐 <b>Did you mean:</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def fuz_click(call):
    _, key, mid, ouid = call.data.split("|")
    if int(call.from_user.id) != int(ouid) and not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "⚠️ Ye aapka request nahi hai!", show_alert=True)
    
    data = db.get_filter(key)
    if data:
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        send_res(call.message, data, int(mid))

def send_res(message, data, r_mid):
    try:
        # Permanent Link
        invite = bot.create_chat_invite_link(int(data['source_cid']), member_limit=0)
        link = invite.invite_link
    except: link = config.LINK_ANIME_CHANNEL
    
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    try:
        bot.copy_message(message.chat.id, config.DB_CHANNEL_ID, int(data['db_mid']), reply_markup=markup, reply_to_message_id=r_mid)
    except:
        bot.send_message(message.chat.id, "❌ Post deleted from DB Channel.", reply_to_message_id=r_mid)
