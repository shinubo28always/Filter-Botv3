from bot_instance import bot
from telebot import types
import utils
import database as db
import config

TEMP_SETUP = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("setup"))
def start_setup(call):
    parts = call.data.split("|")
    TEMP_SETUP[call.from_user.id] = {"source_cid": int(parts[1])}
    msg = bot.send_message(call.from_user.id, "🎬 <b>Enter Anime Name:</b>")
    bot.register_next_step_handler(msg, process_mal)

def process_mal(message):
    uid = message.from_user.id
    info = utils.get_anime_info(message.text)
    if not info: return bot.send_message(uid, "❌ Anime not found on MAL. Try again:")
    
    TEMP_SETUP[uid].update(info)
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ Confirm & Post", callback_data="conf_save"))
    bot.send_photo(uid, info['poster'], caption=info['caption'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "conf_save")
def save_post(call):
    uid = call.from_user.id
    data = TEMP_SETUP.get(uid)
    if not data: return
    
    try:
        # DB Channel mein post karna
        db_msg = bot.send_photo(int(config.DB_CHANNEL_ID), data['poster'], caption=data['caption'])
        TEMP_SETUP[uid]['db_mid'] = db_msg.message_id
        
        msg = bot.send_message(uid, "🔑 <b>Post Success!</b> Now send Keywords (comma separated):")
        bot.register_next_step_handler(msg, finalize_db)
    except Exception as e:
        bot.send_message(uid, f"❌ Permission Error: {e}")

def finalize_db(message):
    uid = message.from_user.id
    kws = [k.strip().lower() for k in message.text.split(",")]
    data = TEMP_SETUP[uid]
    
    for kw in kws:
        db.add_filter(kw, {
            "title": data['title'],
            "db_mid": data['db_mid'],
            "source_cid": data['source_cid']
        })
    bot.send_message(uid, "✅ <b>Filter Added to Database!</b>")
    del TEMP_SETUP[uid]
