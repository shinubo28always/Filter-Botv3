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
    
    # --- 1. FSUB CHECK (PM ONLY) ---
    if message.chat.type == "private":
        fsub_channels = db.get_all_fsub()
        for f in fsub_channels:
            try:
                status = bot.get_chat_member(f['_id'], uid).status
                if status in ['left', 'kicked']:
                    is_req = f['mode'] == "request"
                    expiry = 300 if is_req else 120 
                    invite = bot.create_chat_invite_link(int(f['_id']), expire_date=int(time.time()) + expiry, creates_join_request=is_req, member_limit=1)
                    btn_text = "✨ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ ✨" if is_req else "✨ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ✨"
                    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(btn_text, url=invite.invite_link))
                    return bot.reply_to(message, f"<b>⚠️ Access Denied!</b>\nJoin <b>{f['title']}</b> to use me.", reply_markup=markup)
            except: continue

    # --- 2. SEARCH LOGIC ---
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices: return

    # Hum 10 matches mangte hain taaki duplicates nikalne ke baad bhi kuch bache
    matches = process.extract(query, choices, limit=10)
    best_matches = [m for m in matches if m[1] > 70]
    if not best_matches: return

    # Case A: 95% se upar match (Direct Delivery)
    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
        return

    # Case B: Suggestions (Removing Duplicates)
    markup = types.InlineKeyboardMarkup()
    seen_titles = set() # Unique titles track karne ke liye

    for b in best_matches:
        f_data = db.get_filter(b[0])
        if f_data:
            anime_title = f_data['title']
            # Agar ye anime title pehle nahi dikhaya gaya hai, tabhi button banayein
            if anime_title not in seen_titles:
                cb = f"fuz|{b[0][:20]}|{message.message_id}|{uid}"
                markup.add(types.InlineKeyboardButton(f"🎬 {anime_title}", callback_data=cb))
                seen_titles.add(anime_title) # Title ko 'seen' mark karein
    
    # Agar koi unique match mila ho tabhi reply karein
    if not seen_titles: return

    bot.reply_to(
        message, 
        f"🧐 <b>Hey {message.from_user.first_name}, did you mean:</b>", 
        reply_markup=markup
    )

# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz_click(call):
    _, key, mid, ouid = call.data.split("|")
    if int(call.from_user.id) != int(ouid) and not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "⚠️ Ye aapka request nahi hai!", show_alert=True)
    
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

def send_final_result(message, data, r_mid):
    target_chat = message.chat.id
    try:
        source_id = int(data['source_cid'])
        expire_at = int(time.time()) + 300 
        invite = bot.create_chat_invite_link(chat_id=source_id, expire_date=expire_at, member_limit=1)
        final_link = invite.invite_link
    except:
        final_link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=final_link))
    
    try:
        bot.copy_message(
            chat_id=target_chat,
            from_chat_id=int(config.DB_CHANNEL_ID),
            message_id=int(data['db_mid']),
            reply_markup=markup,
            reply_to_message_id=r_mid
        )
    except Exception as e:
        bot.send_message(target_chat, "❌ <b>Error:</b> Post deleted from DB Channel.", reply_to_message_id=r_mid)
