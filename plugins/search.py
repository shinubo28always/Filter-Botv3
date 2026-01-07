import time
import config
import database as db
from bot_instance import bot
from telebot import types, apihelper
from thefuzz import process
from utils import send_log

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    if message.text.startswith("/"): return
    
    uid = message.from_user.id
    db.add_user(uid)
    
    # --- 1. HARD FSUB LOGIC (PM ONLY) ---
    if message.chat.type == "private":
        all_fsubs = db.get_all_fsub()
        not_joined = []

        for f in all_fsubs:
            try:
                # Force casting to INT for API stability
                f_id = int(f['_id'])
                member = bot.get_chat_member(f_id, uid)
                
                # Check: Agar status in teeno mein se ek bhi HAI, toh user joined hai
                is_joined = member.status in ['member', 'administrator', 'creator']
                
                if not is_joined:
                    not_joined.append(f)
            except Exception as e:
                # Agar bot admin nahi hai ya koi aur error, toh use block hi samjho (Security)
                print(f"DEBUG: FSub API Error: {e}")
                not_joined.append(f)

        # Agar join nahi hai toh buttons dikhao
        if not_joined:
            markup = types.InlineKeyboardMarkup()
            for f in not_joined:
                f_id = int(f['_id'])
                mode = f.get('mode', 'normal')
                is_req = (mode == "request")
                
                try:
                    # Link Expiry: 120s (2 Minutes) | NO member_limit as ordered
                    expiry_time = int(time.time()) + 120 
                    
                    invite = bot.create_chat_invite_link(
                        chat_id=f_id,
                        expire_date=expiry_time,
                        creates_join_request=is_req
                    )
                    
                    link = invite.invite_link
                    btn_text = f"✨ {'Request To Join' if is_req else 'Join Channel'}: {f['title']} ✨"
                    markup.add(types.InlineKeyboardButton(btn_text, url=link))
                except Exception as e:
                    # Professional Error Format
                    return bot.reply_to(
                        message, 
                        f"❌ <b>Error!</b>\n<code>{str(e)}</code>", 
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN)
                        ),
                        parse_mode='HTML'
                    )

            markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))
            join_msg = "<b>👋 Welcome!</b>\n\nResults dekhne ke liye hamare niche diye gaye channels join karein.\n\n<i>Join hone ke baad dobara search karein!</i>"
            return bot.reply_to(message, join_msg, reply_markup=markup, parse_mode='HTML')

    # --- 2. SEARCH ENGINE ---
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices: return

    matches = process.extract(query, choices, limit=10)
    best_matches = [m for m in matches if m[1] > 70]
    if not best_matches: return

    # Case A: Exact Match
    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
        return

    # Case B: Unique Suggestions
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
        source_id = int(data['source_cid'])
        # Permanent link generation for the result button
        invite = bot.create_chat_invite_link(chat_id=source_id, member_limit=0)
        link = invite.invite_link
    except:
        link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    try:
        # NO effects here to prevent crash
        bot.copy_message(
            chat_id=target_chat,
            from_chat_id=int(config.DB_CHANNEL_ID),
            message_id=int(data['db_mid']),
            reply_markup=markup,
            reply_to_message_id=r_mid
        )
    except Exception as e:
        bot.send_message(target_chat, f"❌ <b>Error!</b>\n<code>{str(e)}</code>", reply_to_message_id=r_mid)

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
