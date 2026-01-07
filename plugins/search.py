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
    
    # --- 1. STRICT FSUB CHECK (ONLY IN PM & ONLY ON SEARCH) ---
    if message.chat.type == "private":
        fsub_channels = db.get_all_fsub()
        for f in fsub_channels:
            f_id = int(f['_id'])
            try:
                member = bot.get_chat_member(f_id, uid)
                if member.status not in ['member', 'administrator', 'creator']:
                    raise Exception("NotJoined")
            except Exception as e:
                # Agar join nahi hai ya bot admin nahi hai
                err_text = str(e)
                markup = types.InlineKeyboardMarkup()
                
                if "NotJoined" in err_text or "user not found" in err_text.lower():
                    msg_txt = f"👋 <b>Wait!</b>\n\nSearch results dekhne ke liye pehle hamara channel <b>{f['title']}</b> join karein.\n\nJoin karne ke baad dobara search karein!"
                    try:
                        is_req = f.get('mode') == "request"
                        expiry = 300 if is_req else 120
                        invite = bot.create_chat_invite_link(f_id, expire_date=int(time.time()) + expiry, creates_join_request=is_req, member_limit=1)
                        markup.add(types.InlineKeyboardButton("✨ Join Channel ✨", url=invite.invite_link))
                    except: pass
                else:
                    msg_txt = f"❌ <b>FSub Error!</b>\n\nBot ko channel <b>{f['title']}</b> mein access nahi mil raha.\n\n<code>Error: {err_text}</code>"
                
                markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))
                return bot.reply_to(message, msg_txt, reply_markup=markup, parse_mode='HTML')

    # --- 2. SEARCH LOGIC (FUZZY MATCHING) ---
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
            bot.reply_to(message, f"🧐 <b>Did you mean:</b>", reply_markup=markup)

def send_final_result(message, data, r_mid):
    target_chat = message.chat.id
    try:
        expire_at = int(time.time()) + 300
        invite = bot.create_chat_invite_link(int(data['source_cid']), expire_date=expire_at, member_limit=1)
        link = invite.invite_link
    except: link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    try:
        bot.copy_message(target_chat, int(config.DB_CHANNEL_ID), int(data['db_mid']), reply_markup=markup, reply_to_message_id=r_mid)
    except:
        bot.send_message(target_chat, "❌ <b>Post missing!</b>\nDatabase channel se message dlt ho gaya hai.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz_click(call):
    _, key, mid, ouid = call.data.split("|")
    if int(call.from_user.id) != int(ouid) and not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "⚠️ Ye aapka request nahi hai!", show_alert=True)
    
    data = db.get_filter(key) or db.get_filter(process.extractOne(key, db.get_all_keywords())[0])
    if data:
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        send_final_result(call.message, data, int(mid))
