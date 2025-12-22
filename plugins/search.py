import time
import config
import database as db
from bot_instance import bot
from telebot import types
from thefuzz import process
from utils import send_log

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    if message.text.startswith("/"): return
    
    uid = message.from_user.id
    db.add_user(uid)
    
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices: return

    # Fuzzy Matching (Top 5 matches nikalna)
    matches = process.extract(query, choices, limit=5)
    best_matches = [m for m in matches if m[1] > 60] # 60% se upar wale suggestions

    if not best_matches:
        if message.chat.type == "private":
            bot.reply_to(message, "❌ <b>Result Nahi Mila!</b>\nSpelling check karein ya /request karein.")
        return

    # Case 1: Agar 95% se upar match hai toh Direct Reply (No suggestions)
    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, original_msg_id=message.message_id)
        return

    # Case 2: Agar match kam hai toh Suggestion Buttons dikhana
    markup = types.InlineKeyboardMarkup()
    for b in best_matches:
        f_data = db.get_filter(b[0])
        if f_data:
            # callback_data limit 64 bytes hoti hai, isliye hum keyword aur msg_id bhej rahe hain
            callback_str = f"fuz|{b[0]}|{message.message_id}"
            if len(callback_str) <= 64:
                markup.add(types.InlineKeyboardButton(f"🎬 {f_data['title']}", callback_data=callback_str))
    
    # User ke message par reply karke suggestion pucha jayega
    bot.reply_to(
        message, 
        "🧐 <b>Did you mean one of these?</b>\n👇 Click on the correct anime name:", 
        reply_markup=markup
    )

# Callback Handler for Suggestions
@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuzzy_click(call):
    # Data nikalna: fuz | keyword | original_message_id
    data_parts = call.data.split("|")
    key = data_parts[1]
    original_msg_id = int(data_parts[2])
    
    filter_data = db.get_filter(key)
    if not filter_data:
        bot.answer_callback_query(call.id, "❌ Filter Not Found!", show_alert=True)
        return

    # 1. Suggestion message ko delete karna (Clean Look)
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass

    # 2. Result bhejna original message par reply karke
    send_final_result(call.message, filter_data, original_msg_id=original_msg_id)

def send_final_result(message, data, original_msg_id):
    target_chat = message.chat.id
    
    # 5-MINUTE TEMPORARY LINK GENERATION
    try:
        expire_at = int(time.time()) + 300
        invite = bot.create_chat_invite_link(
            chat_id=int(data['source_cid']), 
            expire_date=expire_at, 
            member_limit=1
        )
        temp_link = invite.invite_link
    except Exception as e:
        send_log(f"❌ Invite Link Error: {e}")
        temp_link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🎬 Watch / Download", url=temp_link)
    )
    
    # COPY FROM DB CHANNEL (Replying to the original search message)
    try:
        bot.copy_message(
            chat_id=target_chat,
            from_chat_id=int(config.DB_CHANNEL_ID),
            message_id=int(data['db_mid']),
            reply_markup=markup,
            reply_to_message_id=original_msg_id # User ke message par reply
        )
    except Exception as e:
        send_log(f"❌ Copy Message Error: {e}\nMID: {data['db_mid']}")
        bot.send_message(target_chat, "❌ <b>Error:</b> Post delete ho chuki hai.", reply_to_message_id=original_msg_id)
