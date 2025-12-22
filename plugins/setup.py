from bot_instance import bot
from telebot import types
import utils
import database as db
import config
import time

TEMP_SETUP = {}

# --- 1. INITIAL STEP: ADD FILTER CLICK ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("setup"))
def init_setup(call):
    parts = call.data.split("|")
    chat_id = int(parts[1])
    chat_title = parts[2]
    uid = call.from_user.id
    
    # Purana message delete karein (Channel Authorized wala)
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass
    
    TEMP_SETUP[uid] = {"source_cid": chat_id, "source_title": chat_title}
    
    # Force Reply ke saath Anime Name maangein
    markup = types.ForceReply(selective=True)
    prompt = bot.send_message(uid, "🎬 <b>Enter Your Anime Name:</b>", reply_markup=markup)
    
    # Prompt ID save karein taaki baad mein delete kar sakein
    TEMP_SETUP[uid]['step1_msg_id'] = prompt.message_id
    bot.register_next_step_handler(prompt, process_anime_name)

# --- 2. STEP: PROCESS NAME & SHOW POSTER ---
def process_anime_name(message):
    uid = message.from_user.id
    if uid not in TEMP_SETUP: return

    anime_name = message.text
    
    # Cleanup: Bot ka prompt aur user ka reply dono delete karein
    try:
        bot.delete_message(uid, TEMP_SETUP[uid]['step1_msg_id'])
        bot.delete_message(uid, message.message_id)
    except: pass

    # Fetch details from MAL
    info = utils.get_anime_info(anime_name)
    if not info:
        # Agar nahi mila toh firse pucho
        markup = types.ForceReply(selective=True)
        re_prompt = bot.send_message(uid, "❌ <b>Anime not found on MAL!</b>\nPlease enter correct name:", reply_markup=markup)
        TEMP_SETUP[uid]['step1_msg_id'] = re_prompt.message_id
        bot.register_next_step_handler(re_prompt, process_anime_name)
        return

    TEMP_SETUP[uid].update(info)
    
    # Poster dikhayein Confirm button ke saath
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("✅ Confirm", callback_data="conf_save"),
        types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_setup")
    )
    poster_msg = bot.send_photo(uid, info['poster'], caption=info['caption'], reply_markup=markup)
    TEMP_SETUP[uid]['poster_msg_id'] = poster_msg.message_id

# --- 3. STEP: CONFIRM POSTER & ASK KEYWORDS ---
@bot.callback_query_handler(func=lambda call: call.data in ["conf_save", "cancel_setup"])
def handle_confirmation(call):
    uid = call.from_user.id
    if uid not in TEMP_SETUP: return

    if call.data == "cancel_setup":
        try: bot.delete_message(uid, call.message.message_id)
        except: pass
        bot.send_message(uid, "❌ Setup Cancelled.")
        del TEMP_SETUP[uid]
        return

    # Poster wala message delete karein
    try: bot.delete_message(uid, call.message.message_id)
    except: pass

    data = TEMP_SETUP[uid]
    
    # DB Channel mein post karna
    try:
        db_msg = bot.send_photo(int(config.DB_CHANNEL_ID), data['poster'], caption=data['caption'])
        TEMP_SETUP[uid]['db_mid'] = db_msg.message_id
        
        # Keywords maangein Force Reply ke saath
        markup = types.ForceReply(selective=True)
        kw_prompt = bot.send_message(
            uid, 
            f"🔑 <b>Enter the filter {data['title']}'s keywords:</b>\n(Comma separated: naruto, s1, hindi)", 
            reply_markup=markup
        )
        TEMP_SETUP[uid]['step2_msg_id'] = kw_prompt.message_id
        bot.register_next_step_handler(kw_prompt, finalize_db)
        
    except Exception as e:
        bot.send_message(uid, f"❌ <b>DB Channel Error:</b> {e}")

# --- 4. FINAL STEP: SAVE & CLEANUP ---
def finalize_db(message):
    uid = message.from_user.id
    if uid not in TEMP_SETUP: return

    keywords = [k.strip().lower() for k in message.text.split(",")]
    data = TEMP_SETUP[uid]
    
    # Cleanup: Bot ka prompt aur user ka reply dono delete karein
    try:
        bot.delete_message(uid, TEMP_SETUP[uid]['step2_msg_id'])
        bot.delete_message(uid, message.message_id)
    except: pass

    # Save to MongoDB
    for kw in keywords:
        db.add_filter(kw, {
            "title": data['title'],
            "db_mid": data['db_mid'],
            "source_cid": data['source_cid']
        })
    
    # Final Success Message
    bot.send_message(uid, f"<b>Filter Has been Added...✔️</b>\n\nAnime: <code>{data['title']}</code>\nKeywords: <code>{', '.join(keywords)}</code>")
    del TEMP_SETUP[uid]
