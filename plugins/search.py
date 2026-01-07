import time
import config
import database as db
from bot_instance import bot
from telebot import types, apihelper
from thefuzz import process

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    if message.text.startswith("/"): return
    
    uid = message.from_user.id
    db.add_user(uid)
    
    # --- 1. LIVE FSUB CHECK (FOR EVERYONE IN PM) ---
    if message.chat.type == "private":
        all_fsubs = db.get_all_fsub()
        for f in all_fsubs:
            try:
                f_id = int(f['_id'])
                # Live status fetch from Telegram
                member = bot.get_chat_member(f_id, uid)
                
                # Check: Creator, Admin, ya Member hai?
                is_authorized = member.status in ['member', 'administrator', 'creator']
                
                if not is_authorized:
                    raise Exception("NotJoined")
            except Exception as e:
                # User joined nahi hai ya link banana hai
                markup = types.InlineKeyboardMarkup()
                is_req = f.get('mode') == "request"
                # Expiry fixed to 2 minutes as requested
                expiry = int(time.time()) + 120 
                
                try:
                    invite = bot.create_chat_invite_link(
                        chat_id=f_id, 
                        expire_date=expiry, 
                        creates_join_request=is_req
                    )
                    link = invite.invite_link
                    # CLEAN BUTTON TEXT
                    btn_text = "✨ Request To Join ✨" if is_req else "✨ Join Channel ✨"
                    markup.add(types.InlineKeyboardButton(btn_text, url=link))
                except:
                    # Fallback only if invite link fails
                    pass

                markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))
                
                err_code = str(e)
                if "NotJoined" in err_code or "user not found" in err_code.lower():
                    msg_txt = f"<b>⚠️ Access Denied!</b>\n\nSearch results dekhne ke liye pehle hamara channel <b>{f['title']}</b> join karein.\n\n<i>Join karne ke baad dobara search karein!</i>"
                else:
                    msg_txt = f"❌ <b>Error!</b>\n<code>{err_code}</code>"
                
                return bot.reply_to(message, msg_txt, reply_markup=markup, parse_mode='HTML')

    # --- 2. SEARCH ENGINE ---
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices: return

    matches = process.extract(query, choices, limit=10)
    best_matches = [m for m in matches if m[1] > 70]
    if not best_matches: return

    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
        return

    # Suggestions Logic
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
    try:
        # Link generator for the result button
        invite = bot.create_chat_invite_link(int(data['source_cid']), member_limit=0)
        link = invite.invite_link
    except:
        link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    try:
        bot.copy_message(message.chat.id, int(config.DB_CHANNEL_ID), int(data['db_mid']), reply_markup=markup, reply_to_message_id=r_mid)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>Error!</b>\n<code>{str(e)}</code>", reply_to_message_id=r_mid)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz_click(call):
    _, key, mid, ouid = call.data.split("|")
    # EVERYONE Check: Even Admins must be the original searcher or authorized
    if int(call.from_user.id) != int(ouid) and not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "⚠️ Ye aapka request nahi hai!", show_alert=True)
    
    # Re-verify FSub status before allowing callback result
    uid = call.from_user.id
    fsub_channels = db.get_all_fsub()
    for f in fsub_channels:
        try:
            st = bot.get_chat_member(int(f['_id']), uid).status
            if st not in ['member', 'administrator', 'creator']:
                return bot.answer_callback_query(call.id, "⚠️ Pehle FSub join karein!", show_alert=True)
        except: pass

    data = db.get_filter(key) or db.get_filter(process.extractOne(key, db.get_all_keywords())[0])
    if data:
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        send_final_result(call.message, data, int(mid))
