### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

from bot_instance import bot
from telebot import types
import utils, database as db, config, html

TEMP_SETUP = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("setup"))
def init_setup(call):
    uid = call.from_user.id
    cid = int(call.data.split("|")[1])
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    
    TEMP_SETUP[uid] = {"source_cid": cid}
    markup = types.ForceReply(selective=True)
    prompt = bot.send_message(uid, "🎬 <b>Enter Your Anime Name:</b>", reply_markup=markup)
    TEMP_SETUP[uid]['m1'] = prompt.message_id
    bot.register_next_step_handler(prompt, search_and_show_options)

def search_and_show_options(message):
    uid = message.from_user.id
    if uid not in TEMP_SETUP: return
    try:
        bot.delete_message(uid, TEMP_SETUP[uid]['m1'])
        bot.delete_message(uid, message.message_id)
    except: pass
    
    results = utils.search_anilist(message.text)
    if not results:
        m = bot.send_message(uid, "❌ Not Found. Send Name Again:", reply_markup=types.ForceReply())
        TEMP_SETUP[uid]['m1'] = m.message_id
        bot.register_next_step_handler(m, search_and_show_options)
        return

    markup = types.InlineKeyboardMarkup()
    for ani in results:
        title = ani['title']['english'] or ani['title']['romaji']
        format_type = ani.get('format', 'N/A')
        # Button text format: [MOVIE] One Piece Red
        markup.add(types.InlineKeyboardButton(f"[{format_type}] {title}", callback_data=f"pick_ani|{ani['id']}"))
    
    markup.add(types.InlineKeyboardButton("❌ Cancel Setup", callback_data="cancel_setup"))
    m = bot.send_message(uid, "🧐 <b>Multiple results found! Choose the correct one:</b>", reply_markup=markup)
    TEMP_SETUP[uid]['m_choice'] = m.message_id

@bot.callback_query_handler(func=lambda call: call.data.startswith("pick_ani|"))
def pick_anime(call):
    uid = call.from_user.id
    ani_id = int(call.data.split("|")[1])
    if uid not in TEMP_SETUP: return
    
    try: bot.delete_message(uid, call.message.message_id)
    except: pass
    
    info = utils.get_anime_details(ani_id)
    if not info:
        return bot.send_message(uid, "❌ Error fetching details. Try again.")

    TEMP_SETUP[uid].update(info)
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ Confirm & Post", callback_data="conf_save"))
    p = bot.send_photo(uid, info['poster'], caption=info['caption'], reply_markup=markup, parse_mode='HTML')
    TEMP_SETUP[uid]['m2'] = p.message_id

@bot.callback_query_handler(func=lambda call: call.data == "conf_save")
def conf_save(call):
    uid = call.from_user.id
    if uid not in TEMP_SETUP: return
    try: bot.delete_message(uid, call.message.message_id)
    except: pass
    
    data = TEMP_SETUP[uid]
    try:
        db_msg = bot.send_photo(config.DB_CHANNEL_ID, data['poster'], caption=data['caption'], parse_mode='HTML')
        TEMP_SETUP[uid]['db_mid'] = db_msg.message_id
        m = bot.send_message(uid, f"🔑 <b>Enter {html.escape(data['title'])}'s keywords:</b>", reply_markup=types.ForceReply())
        TEMP_SETUP[uid]['m3'] = m.message_id
        bot.register_next_step_handler(m, finalize)
    except Exception as e:
        bot.send_message(uid, f"❌ <b>Error:</b> {e}")

def finalize(message):
    uid = message.from_user.id
    if uid not in TEMP_SETUP: return
    kws = [k.strip().lower() for k in message.text.split(",")]
    try:
        bot.delete_message(uid, TEMP_SETUP[uid]['m3'])
        bot.delete_message(uid, message.message_id)
    except: pass
    
    data = TEMP_SETUP[uid]
    for k in kws:
        db.add_filter(k, {"title": data['title'], "db_mid": data['db_mid'], "source_cid": data['source_cid']})
    bot.send_message(uid, f"<b>Filter Has been Added...✔️</b>\n\nAnime: <code>{html.escape(data['title'])}</code>", parse_mode='HTML')
    del TEMP_SETUP[uid]

@bot.callback_query_handler(func=lambda call: call.data == "cancel_setup")
def cancel_setup(call):
    uid = call.from_user.id
    if uid in TEMP_SETUP: del TEMP_SETUP[uid]
    bot.edit_message_text("❌ Setup Cancelled.", call.message.chat.id, call.message.message_id)
