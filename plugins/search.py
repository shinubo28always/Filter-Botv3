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
    db.add_user(uid) # Save user for broadcast tracking
    
    # --- 1. FSUB CHECK (ONLY IN PRIVATE CHAT) ---
    if message.chat.type == "private":
        fsub_channels = db.get_all_fsub()
        for f in fsub_channels:
            try:
                status = bot.get_chat_member(f['_id'], uid).status
                if status in ['left', 'kicked']:
                    is_req = f['mode'] == "request"
                    # Expiry Logic: Request (5m = 300s), Normal (2m = 120s)
                    expiry = 300 if is_req else 120 
                    
                    invite = bot.create_chat_invite_link(
                        chat_id=int(f['_id']),
                        expire_date=int(time.time()) + expiry,
                        creates_join_request=is_req,
                        member_limit=1
                    )
                    
                    btn_text = "✨ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ ✨" if is_req else "✨ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ✨"
                    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(btn_text, url=invite.invite_link))
                    return bot.reply_to(
                        message, 
                        f"<b>⚠️ Access Denied!</b>\n\nSearch result dekhne ke liye hamara channel <b>{f['title']}</b> join karein.", 
                        reply_markup=markup
                    )
            except: continue

    # --- 2. SEARCH LOGIC (FUZZY MATCHING) ---
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices: return

    matches = process.extract(query, choices, limit=5)
    best_matches = [m for m in matches if m[1] > 70] # 70% accuracy threshold
    if not best_matches: return

    # Case A: Perfect Match (Direct Delivery)
    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
        return

    # Case B: Multiple Suggestions with User Lock
    markup = types.InlineKeyboardMarkup()
    for b in best_matches:
        f_data = db.get_filter(b[0])
        if f_data:
            # Format: fuz | key_shortcut | original_msg_id | searcher_uid
            # Keyword 20 chars tak truncate kiye taaki callback 64 bytes se chota rahe
            cb_data = f"fuz|{b[0][:20]}|{message.message_id}|{uid}"
            markup.add(types.InlineKeyboardButton(f"🎬 {f_data['title']}", callback_data=cb_data))
    
    bot.reply_to(
        message, 
        f"🧐 <b>Hey {message.from_user.first_name}, did you mean:</b>", 
        reply_markup=markup
    )

# --- SUGGESTION CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz_click(call):
    _, key, mid, original_uid = call.data.split("|")
    clicker_uid = call.from_user.id

    # 🛑 USER-LOCK CHECK: Sirf searcher ya admin click kar sakega
    if clicker_uid != int(original_uid) and not db.is_admin(clicker_uid):
        return bot.answer_callback_query(
            call.id, 
            "⚠️ Ye aapka request nahi hai!\nApna khud ka anime search karein.", 
            show_alert=True
        )

    # Permission granted, result fetch karein
    data = db.get_filter(key)
    if not data:
        # Fallback if key was truncated
        choices = db.get_all_keywords()
        matches = process.extract(key, choices, limit=1)
        if matches: data = db.get_filter(matches[0][0])

    if data:
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        send_final_result(call.message, data, int(mid))

# --- FINAL RESULT DELIVERY ---
def send_final_result(message, data, r_mid):
    try:
        # Source Channel Invite Link (Permanent result link)
        invite = bot.create_chat_invite_link(int(data['source_cid']), member_limit=0)
        link = invite.invite_link
    except: link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    
    try:
        # Copy original post from DB channel
        bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=int(config.DB_CHANNEL_ID),
            message_id=int(data['db_mid']),
            reply_markup=markup,
            reply_to_message_id=r_mid # Reply specifically to user's search text
        )
    except Exception as e:
        send_log(f"❌ Result Delivery Error: {e}\nMID: {data['db_mid']}")
        bot.send_message(message.chat.id, "❌ <b>Post missing!</b> Link DB channel se delete ho chuka hai.", reply_to_message_id=r_mid)
