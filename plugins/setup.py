from bot_instance import bot
from telebot import types
import utils
import database as db
import config

TEMP_FLOW = {}

@bot.callback_query_handler(func=lambda call: call.data.startswith("setup"))
def start_setup(call):
    # Data format: setup|chat_id|title
    parts = call.data.split("|")
    cid = int(parts[1])
    title = parts[2]
    
    TEMP_FLOW[call.from_user.id] = {"source_cid": cid}
    msg = bot.send_message(call.from_user.id, f"🎬 <b>Setting up for:</b> {title}\n\nAb Anime ka naam bhejein:")
    bot.register_next_step_handler(msg, process_anime_name)

def process_anime_name(message):
    uid = message.from_user.id
    info = utils.get_anime_info(message.text)
    
    if not info:
        return bot.send_message(uid, "❌ MAL par nahi mila. Dobara sahi naam bhejein:")
    
    TEMP_FLOW[uid].update(info)
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ Confirm & Post", callback_data="confirm_final"))
    bot.send_photo(uid, info['poster'], caption=info['details'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "confirm_final")
def finalize_post(call):
    uid = call.from_user.id
    if uid not in TEMP_FLOW: return
    
    data = TEMP_FLOW[uid]
    
    # DB Channel mein post karna
    try:
        db_msg = bot.send_photo(int(config.DB_CHANNEL_ID), data['poster'], caption=data['details'])
        TEMP_FLOW[uid]['db_mid'] = db_msg.message_id
        
        msg = bot.send_message(uid, "🔑 <b>Post Success!</b>\n\nAb Keywords bhejein (comma separated):\nExample: <code>naruto, s1, shippuden</code>")
        bot.register_next_step_handler(msg, save_all_data)
    except Exception as e:
        bot.send_message(uid, f"❌ DB Channel Error: {e}\nCheck karein ki bot DB channel mein admin hai.")

def save_all_data(message):
    uid = message.from_user.id
    keywords = [k.strip().lower() for k in message.text.split(",")]
    data = TEMP_FLOW[uid]
    
    for kw in keywords:
        db.add_filter(kw, {
            "title": data['title'],
            "db_mid": int(data['db_mid']),
            "source_cid": int(data['source_cid'])
        })
    
    bot.send_message(uid, f"✅ <b>Filter Saved!</b>\nKeywords: {', '.join(keywords)}")
    del TEMP_FLOW[uid]
