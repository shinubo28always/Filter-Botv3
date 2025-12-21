import time
from bot_instance import bot
from telebot import types
import database as db
import config
from thefuzz import process

@bot.message_handler(func=lambda m: True)
def search_handler(message):
    if message.text.startswith("/"): return
    uid = message.from_user.id
    db.add_user(uid)
    
    # FSub Check
    fsub_id = db.get_fsub()
    if fsub_id:
        try:
            status = bot.get_chat_member(fsub_id, uid).status
            if status not in ['member', 'administrator', 'creator']:
                link = bot.create_chat_invite_link(fsub_id).invite_link
                markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Join Channel", url=link))
                return bot.reply_to(message, "<b>Join First!</b>", reply_markup=markup)
        except: pass

    query = message.text.lower()
    choices = db.get_all_keywords()
    if not choices: return

    matches = process.extract(query, choices, limit=3)
    best = [m for m in matches if m[1] > 75]

    if not best: return

    if best[0][1] == 100:
        send_res(message, db.get_filter(best[0][0]))
    else:
        markup = types.InlineKeyboardMarkup()
        for b in best:
            f_data = db.get_filter(b[0])
            markup.add(types.InlineKeyboardButton(f_data['title'], callback_data=f"fuz|{b[0]}"))
        bot.reply_to(message, "🧐 <b>Did you mean:</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz(call):
    key = call.data.split("|")[1]
    send_res(call.message, db.get_filter(key), is_cb=True)

def send_res(message, data, is_cb=False):
    try:
        # Generate 5-min link
        link = bot.create_chat_invite_link(data['source_cid'], expire_date=int(time.time())+300, member_limit=1).invite_link
    except: link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    
    bot.copy_message(
        chat_id=message.chat.id,
        from_chat_id=config.DB_CHANNEL_ID,
        message_id=data['db_mid'],
        reply_markup=markup,
        message_effect_id=config.EFFECT_PARTY
    )
    if is_cb: bot.delete_message(message.chat.id, message.message_id)
