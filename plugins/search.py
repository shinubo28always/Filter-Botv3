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
    
    # --- 1. FSUB CHECK (STRICT - PM ONLY) ---
    if message.chat.type == "private":
        fsub_channels = db.get_all_fsub()
        for f in fsub_channels:
            try:
                # Ensure ID is integer for Telegram API
                f_id = int(f['_id'])
                member = bot.get_chat_member(f_id, uid)
                
                # Agar user Joined nahi hai (left, kicked, ya restricted)
                if member.status not in ['member', 'administrator', 'creator']:
                    raise Exception("Not Joined")
            except Exception:
                # Link Generation Logic
                is_req = f.get('mode') == "request"
                expiry = 300 if is_req else 120 
                
                try:
                    invite = bot.create_chat_invite_link(
                        chat_id=int(f['_id']),
                        expire_date=int(time.time()) + expiry,
                        creates_join_request=is_req,
                        member_limit=1
                    )
                    link = invite.invite_link
                except:
                    link = config.LINK_ANIME_CHANNEL # Fallback

                btn_text = "✨ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ ✨" if is_req else "✨ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ✨"
                markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(btn_text, url=link))
                
                return bot.reply_to(
                    message, 
                    f"<b>⚠️ Access Denied!</b>\n\nSearch results dekhne ke liye hamara channel <b>{f['title']}</b> join karna zaroori hai.\n\n👇 Niche button par click karke join karein:", 
                    reply_markup=markup,
                    parse_mode='HTML'
                )

    # --- 2. SEARCH LOGIC ---
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices: return

    matches = process.extract(query, choices, limit=10)
    best_matches = [m for m in matches if m[1] > 70]
    if not best_matches: return

    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
    else:
        markup = types.InlineKeyboardMarkup()
        seen_titles = set()
        for b in best_matches:
            f_data = db.get_filter(b[0])
            if f_data and f_data['title'] not in seen_titles:
                cb = f"fuz|{b[0][:20]}|{message.message_id}|{uid}"
                markup.add(types.InlineKeyboardButton(f"🎬 {f_data['title']}", callback_data=cb))
                seen_titles.add(f_data['title'])
        
        if seen_titles:
            bot.reply_to(message, f"🧐 <b>Hey {message.from_user.first_name}, did you mean:</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz_click(call):
    _, key, mid, ouid = call.data.split("|")
    if int(call.from_user.id) != int(ouid) and not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "⚠️ Ye aapka request nahi hai!", show_alert=True)
    
    data = db.get_filter(key)
    if data:
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        send_final_result(call.message, data, int(mid))

def send_final_result(message, data, r_mid):
    try:
        expire_at = int(time.time()) + 300
        invite = bot.create_chat_invite_link(int(data['source_cid']), expire_date=expire_at, member_limit=1)
        link = invite.invite_link
    except: link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    try:
        bot.copy_message(message.chat.id, int(config.DB_CHANNEL_ID), int(data['db_mid']), reply_markup=markup, reply_to_message_id=r_mid)
    except:
        bot.send_message(message.chat.id, "❌ <b>Post missing!</b>\nDatabase channel se message dlt ho gaya hai.")
