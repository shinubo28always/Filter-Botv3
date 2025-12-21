from bot_instance import bot
from telebot import types
import utils
import database as db
import config

TEMP_FLOW = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("setup"))
def start_setup(call):
    _, cid, title = call.data.split("|")
    TEMP_FLOW[call.from_user.id] = {"source_cid": cid}
    msg = bot.send_message(call.from_user.id, "🎬 <b>Enter Anime Name:</b>")
    bot.register_next_step_handler(msg, process_name)

def process_name(message):
    uid = message.from_user.id
    info = utils.get_anime_info(message.text)
    if not info: return bot.send_message(uid, "❌ Not found. Try again.")
    
    TEMP_FLOW[uid].update(info)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Confirm", callback_data="confirm_db"))
    bot.send_photo(uid, info['poster'], caption=info['details'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_db")
def save_db_chnl(call):
    uid = call.from_user.id
    data = TEMP_FLOW[uid]
    db_msg = bot.send_photo(config.DB_CHANNEL_ID, data['poster'], caption=data['details'])
    TEMP_FLOW[uid]['db_mid'] = db_msg.message_id
    
    msg = bot.send_message(uid, "🔑 <b>Send Keywords (comma separated):</b>")
    bot.register_next_step_handler(msg, save_final)

def save_final(message):
    uid = message.from_user.id
    kws = [k.strip().lower() for k in message.text.split(",")]
    data = TEMP_FLOW[uid]
    
    for k in kws:
        db.add_filter(k, {"title": data['title'], "db_mid": data['db_mid'], "source_cid": data['source_cid']})
    
    bot.send_message(uid, "✅ Saved in MongoDB!")
    del TEMP_FLOW[uid]
