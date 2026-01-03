import time
import config
import database as db
from bot_instance import bot
from telebot import types, apihelper
from thefuzz import process
from utils import send_log

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    # Command check
    if message.text.startswith("/"): return
    
    uid = message.from_user.id
    db.add_user(uid) # Broadcast ke liye user save karna
    
    # --- 1. FSUB CHECK (ONLY IN PRIVATE CHAT) ---
    if message.chat.type == "private":
        fsub_channels = db.get_all_fsub()
        for f in fsub_channels:
            try:
                # Ensure ID is integer
                f_id = int(f['_id'])
                member = bot.get_chat_member(f_id, uid)
                
                # Agar user joined nahi hai
                if member.status not in ['member', 'administrator', 'creator']:
                    raise Exception("Not Joined")
            except Exception as e:
                err_msg = str(e)
                markup = types.InlineKeyboardMarkup()
                
                # Text logic
                if "Not Joined" in err_msg:
                    final_txt = f"<b>👋 Welcome!</b>\n\nBot use karne ke liye hamara channel <b>{f['title']}</b> join karein."
                else:
                    # Bot access error (Like bot removed from chnl)
                    final_txt = f"❌ <b>FSub Access Error!</b>\n<code>{err_msg}</code>\n\nAdmin ko report karein."
                    markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))

                # Try to generate join link
                try:
                    is_req = f.get('mode') == "request"
                    expiry = 300 if is_req else 120 
                    invite = bot.create_chat_invite_link(
                        chat_id=int(f['_id']),
                        expire_date=int(time.time()) + expiry,
                        creates_join_request=is_req,
                        member_limit=1
                    )
                    btn_txt = "✨ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ ✨" if is_req else "✨ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ✨"
                    markup.add(types.InlineKeyboardButton(btn_txt, url=invite.invite_link))
                except: pass
                
                return bot.reply_to(message, final_txt, reply_markup=markup, parse_mode='HTML')

    # --- 2. SEARCH LOGIC (FUZZY MATCHING) ---
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices: return

    matches = process.extract(query, choices, limit=10)
    best_matches = [m for m in matches if m[1] > 70]
    if not best_matches: return

    # Case A: Perfect Match (Direct Result)
    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
        return

    # Case B: Suggestions with User Lock
    markup = types.InlineKeyboardMarkup()
    seen_titles = set()
    for b in best_matches:
        f_data = db.get_filter(b[0])
        if f_data and f_data['title'] not in seen_titles:
            # CB format: fuz | keyword | original_msg_id | searcher_uid
            cb_data = f"fuz|{b[0][:20]}|{message.message_id}|{uid}"
            markup.add(types.InlineKeyboardButton(f"🎬 {f_data['title']}", callback_data=cb_data))
            seen_titles.add(f_data['title'])
    
    if seen_titles:
        bot.reply_to(
            message, 
            f"🧐 <b>Hey {message.from_user.first_name}, did you mean:</b>", 
            reply_markup=markup,
            parse_mode='HTML'
        )

# --- CALLBACK HANDLER FOR SUGGESTIONS ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz_click(call):
    _, key, mid, original_uid = call.data.split("|")
    clicker_uid = call.from_user.id

    # 🛑 USER-LOCK CHECK with Popup
    if clicker_uid != int(original_uid) and not db.is_admin(clicker_uid):
        return bot.answer_callback_query(
            call.id, 
            "⚠️ Ye aapka request nahi hai!\nApna khud ka anime search karein.", 
            show_alert=True
        )

    # Permission granted, result fetch karein
    data = db.get_filter(key)
    if not data:
        # Keyword truncated tha toh dobara search
        choices = db.get_all_keywords()
        matches = process.extract(key, choices, limit=1)
        if matches: data = db.get_filter(matches[0][0])

    if data:
        # Cleanup suggestion
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        send_final_result(call.message, data, int(mid))

# --- FINAL RESULT DELIVERY ---
def send_final_result(message, data, r_mid):
    target_chat = message.chat.id
    
    # 1. 5-MINUTE DYNAMIC INVITE LINK
    try:
        expire_at = int(time.time()) + 300 
        invite = bot.create_chat_invite_link(
            chat_id=int(data['source_cid']), 
            expire_date=expire_at, 
            member_limit=1
        )
        temp_link = invite.invite_link
    except Exception as e:
        print(f"Invite Gen Error: {e}")
        temp_link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🎬 Watch / Download", url=temp_link)
    )
    
    # 2. COPY FROM DB CHANNEL (NO EFFECTS - TO PREVENT CRASH)
    try:
        bot.copy_message(
            chat_id=target_chat,
            from_chat_id=int(config.DB_CHANNEL_ID),
            message_id=int(data['db_mid']),
            reply_markup=markup,
            reply_to_message_id=r_mid 
        )
    except Exception as e:
        send_log(f"❌ Result Delivery Error: {e}\nMID: {data['db_mid']}")
        bot.send_message(target_chat, "❌ <b>Post missing!</b>\nAdmin ko report karein.", reply_to_message_id=r_mid)
