import time
from bot_instance import bot
from telebot import types
import database as db
import config
from thefuzz import process

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    if message.text.startswith("/"): return
    uid = message.from_user.id
    db.add_user(uid)
    
    # FSub Check
    fid = db.get_fsub()
    if fid:
        try:
            st = bot.get_chat_member(fid, uid).status
            if st not in ['member', 'administrator', 'creator']:
                lk = bot.create_chat_invite_link(fid).invite_link
                btn = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Join Channel", url=lk))
                return bot.reply_to(message, "<b>Join First!</b>", reply_markup=btn)
        except: pass

    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices: return

    matches = process.extract(query, choices, limit=3)
    best = [m for m in matches if m[1] > 70]
    if not best: return

    if best[0][1] >= 95:
        send_res(message, db.get_filter(best[0][0]))
    else:
        markup = types.InlineKeyboardMarkup()
        for b in best:
            markup.add(types.InlineKeyboardButton(db.get_filter(b[0])['title'], callback_data=f"fuz|{b[0]}"))
        bot.reply_to(message, "🧐 <b>Did you mean:</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz(call):
    key = call.data.split("|")[1]
    send_res(call.message, db.get_filter(key), is_cb=True)

def send_res(message, data, is_cb=False):
    target = message.chat.id
    try:
        # Temporary 5-min link
        invite = bot.create_chat_invite_link(int(data['source_cid']), expire_date=int(time.time())+300, member_limit=1)
        link = invite.invite_link
    except: link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    try:
        bot.copy_message(target, config.DB_CHANNEL_ID, data['db_mid'], reply_markup=markup, message_effect_id=config.EFFECT_PARTY)
    except: bot.send_message(target, "❌ Error: Link expired or DB message deleted.")
    if is_cb: bot.delete_message(target, message.message_id)
