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

    # Fuzzy Matching
    matches = process.extract(query, choices, limit=5)
    best_matches = [m for m in matches if m[1] > 60]

    if not best_matches:
        if message.chat.type == "private":
            bot.reply_to(message, "❌ <b>Result Nahi Mila!</b>")
        return

    # Case 1: Direct Match (>= 95%)
    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, original_msg_id=message.message_id)
        return

    # Case 2: Suggestions with User-Lock
    markup = types.InlineKeyboardMarkup()
    for b in best_matches:
        f_data = db.get_filter(b[0])
        if f_data:
            # Data format: fuz | keyword_shortcut | user_msg_id | searcher_id
            # 64 bytes limit ke liye keyword ko truncate kiya hai
            short_key = b[0][:20]
            cb_data = f"fuz|{short_key}|{message.message_id}|{uid}"
            markup.add(types.InlineKeyboardButton(f"🎬 {f_data['title']}", callback_data=cb_data))
    
    bot.reply_to(
        message, 
        f"🧐 <b>Hey {message.from_user.first_name}, did you mean:</b>", 
        reply_markup=markup
    )

# --- CALLBACK HANDLER WITH POPUP LOGIC ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuzzy_click(call):
    # Data nikalna
    _, key, mid, original_uid = call.data.split("|")
    
    clicker_id = call.from_user.id
    original_uid = int(original_uid)
    original_msg_id = int(mid)

    # 🛑 PERMISSION CHECK (Searcher OR Admin OR Owner)
    if clicker_id != original_uid and not db.is_admin(clicker_id):
        # DUSRE BANDE KO POPUP DIKHANA
        bot.answer_callback_query(
            call.id, 
            "⚠️ Ye aapka request nahi hai!\nApna khud ka anime search karein.", 
            show_alert=True # Isse popup message aayega
        )
        return

    # ✅ Permission granted - Filter dhundna
    filter_data = db.get_filter(key)
    if not filter_data:
        # Agar keyword shortcut ki wajah se na mile toh fuzzy search dobara karein
        choices = db.get_all_keywords()
        matches = process.extract(key, choices, limit=1)
        if matches: filter_data = db.get_filter(matches[0][0])

    if not filter_data:
        bot.answer_callback_query(call.id, "❌ Filter detail nahi mili!", show_alert=True)
        return

    # 🗑️ Suggestion message delete karna
    try: bot.delete_message(call.message.chat.id, call.message.message_id)
    except: pass

    # 🎬 Result bhejna (Reply to original message)
    send_final_result(call.message, filter_data, original_msg_id=original_msg_id)

def send_final_result(message, data, original_msg_id):
    target_chat = message.chat.id
    
    # 5-Min Temp Link
    try:
        expire_at = int(time.time()) + 300
        invite = bot.create_chat_invite_link(
            chat_id=int(data['source_cid']), 
            expire_date=expire_at, 
            member_limit=1
        )
        temp_link = invite.invite_link
    except:
        temp_link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🎬 Watch / Download", url=temp_link)
    )
    
    # Copy from DB Channel as a reply
    try:
        bot.copy_message(
            chat_id=target_chat,
            from_chat_id=int(config.DB_CHANNEL_ID),
            message_id=int(data['db_mid']),
            reply_markup=markup,
            reply_to_message_id=original_msg_id 
        )
    except Exception as e:
        send_log(f"❌ Result Delivery Error: {e}")
        bot.send_message(target_chat, "❌ <b>Error:</b> Post mil nahi rahi.", reply_to_message_id=original_msg_id)
