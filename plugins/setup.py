from bot_instance import bot
from telebot import types
import utils, database as db, config

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
    bot.register_next_step_handler(prompt, get_name)

def get_name(message):
    uid = message.from_user.id
    if uid not in TEMP_SETUP: return
    try:
        bot.delete_message(uid, TEMP_SETUP[uid]['m1'])
        bot.delete_message(uid, message.message_id)
    except: pass
    
    info = utils.get_anime_info(message.text)
    if not info:
        m = bot.send_message(uid, "❌ Not Found. Send Name Again:", reply_markup=types.ForceReply())
        TEMP_SETUP[uid]['m1'] = m.message_id
        bot.register_next_step_handler(m, get_name)
        return
    
    TEMP_SETUP[uid].update(info)
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ Confirm", callback_data="conf_save"))
    p = bot.send_photo(uid, info['poster'], caption=info['caption'], reply_markup=markup)
    TEMP_SETUP[uid]['m2'] = p.message_id

@bot.callback_query_handler(func=lambda call: call.data == "conf_save")
def conf_save(call):
    uid = call.from_user.id
    if uid not in TEMP_SETUP: return
    try: bot.delete_message(uid, call.message.message_id)
    except: pass
    
    data = TEMP_SETUP[uid]
    db_msg = bot.send_photo(config.DB_CHANNEL_ID, data['poster'], caption=data['caption'])
    TEMP_SETUP[uid]['db_mid'] = db_msg.message_id
    
    m = bot.send_message(uid, f"🔑 <b>Enter {data['title']}'s keywords:</b>", reply_markup=types.ForceReply())
    TEMP_SETUP[uid]['m3'] = m.message_id
    bot.register_next_step_handler(m, finalize)

def finalize(message):
    uid = message.from_user.id
    kws = [k.strip().lower() for k in message.text.split(",")]
    try:
        bot.delete_message(uid, TEMP_SETUP[uid]['m3'])
        bot.delete_message(uid, message.message_id)
    except: pass
    
    data = TEMP_SETUP[uid]
    for k in kws:
        db.add_filter(k, {"title": data['title'], "db_mid": data['db_mid'], "source_cid": data['source_cid']})
    bot.send_message(uid, "<b>Filter Has been Added...✔️</b>")
    del TEMP_SETUP[uid]
