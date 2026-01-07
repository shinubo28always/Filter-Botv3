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
    
    # --- 1. FSUB LOGIC (ONLY IN PM) ---
    if message.chat.type == "private":
        all_fsubs = db.get_all_fsub()
        not_joined = []

        # Check karein kaunsa channel join nahi hai
        for f in all_fsubs:
            try:
                member = bot.get_chat_member(int(f['_id']), uid)
                if member.status not in ['member', 'administrator', 'creator']:
                    not_joined.append(f)
            except Exception:
                not_joined.append(f)

        # Agar ek bhi join nahi hai, toh saare buttons dikhao
        if not_joined:
            markup = types.InlineKeyboardMarkup()
            for f in all_fsubs:
                f_id = int(f['_id'])
                mode = f.get('mode', 'normal')
                is_req = mode == "request"
                
                try:
                    # Link Generation based on Mode
                    expiry = 300 if is_req else 120
                    invite = bot.create_chat_invite_link(
                        chat_id=f_id,
                        expire_date=int(time.time()) + expiry,
                        creates_join_request=is_req,
                        member_limit=1
                    )
                    link = invite.invite_link
                    btn_text = f"✨ {'Request To Join' if is_req else 'Join Channel'}: {f['title']} ✨"
                    markup.add(types.InlineKeyboardButton(btn_text, url=link))
                except Exception as e:
                    # Agar link fail ho toh error msg formatting
                    return bot.reply_to(
                        message, 
                        f"❌ <b>Error!</b>\n<code>{str(e)}</code>", 
                        reply_markup=types.InlineKeyboardMarkup().add(
                            types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN)
                        ),
                        parse_mode='HTML'
                    )

            # Extra Support Button
            markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))
            
            join_msg = "<b>👋 Welcome!</b>\n\nResults dekhne ke liye hamare niche diye gaye channels join karein.\n\n<i>Join hone ke baad dobara search karein!</i>"
            return bot.reply_to(message, join_msg, reply_markup=markup, parse_mode='HTML')

    # --- 2. SEARCH LOGIC (FOR GROUPS & AUTHORIZED PM) ---
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

def send_final_result(message, data, r_mid):
    target_chat = message.chat.id
    try:
        source_id = int(data['source_cid'])
        invite = bot.create_chat_invite_link(chat_id=source_id, expire_date=int(time.time())+300, member_limit=1)
        link = invite.invite_link
    except:
        link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    try:
        bot.copy_message(target_chat, int(config.DB_CHANNEL_ID), int(data['db_mid']), reply_markup=markup, reply_to_message_id=r_mid)
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
