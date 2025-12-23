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
    
    # --- FSUB CHECK (ONLY IN PM) ---
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

    # --- SEARCH LOGIC ---
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices: return

    matches = process.extract(query, choices, limit=5)
    best = [m for m in matches if m[1] > 70]
    if not best: return

    if best[0][1] >= 95:
        data = db.get_filter(best[0][0])
        send_final_result(message, data, message.message_id)
    else:
        markup = types.InlineKeyboardMarkup()
        for b in best:
            f_data = db.get_filter(b[0])
            if f_data:
                cb = f"fuz|{b[0][:20]}|{message.message_id}|{uid}"
                markup.add(types.InlineKeyboardButton(f"🎬 {f_data['title']}", callback_data=cb))
        bot.reply_to(message, f"🧐 <b>Hey {message.from_user.first_name}, did you mean:</b>", reply_markup=markup)

# ... (send_final_result and handle_fuzzy remain same) ...
