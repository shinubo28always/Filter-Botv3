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
    
    # --- 1. FSUB CHECK WITH DYNAMIC LINK FIX (PM ONLY) ---
    if message.chat.type == "private":
        fsub_channels = db.get_all_fsub()
        for f in fsub_channels:
            f_id = int(f['_id'])
            try:
                member = bot.get_chat_member(f_id, uid)
                if member.status not in ['member', 'administrator', 'creator']:
                    raise Exception("NotJoined")
            except Exception as e:
                # Agar user join nahi hai ya bot admin nahi hai
                markup = types.InlineKeyboardMarkup()
                is_req = f.get('mode') == "request"
                
                # --- DYNAMIC LINK LOGIC (Fixing the wrong link error) ---
                fsub_invite_link = None
                
                try:
                    # Method 1: Try to create a temporary invite link
                    expiry = 300 if is_req else 120
                    invite = bot.create_chat_invite_link(
                        chat_id=f_id, 
                        expire_date=int(time.time()) + expiry, 
                        creates_join_request=is_req, 
                        member_limit=1
                    )
                    fsub_invite_link = invite.invite_link
                except:
                    # Method 2: Fallback to Public Username link if Method 1 fails
                    try:
                        chat_data = bot.get_chat(f_id)
                        if chat_data.username:
                            fsub_invite_link = f"https://t.me/{chat_data.username}"
                    except: pass

                # Final Verification: Agar link abhi bhi nahi mila toh anime channel mat dena
                if not fsub_invite_link:
                    fsub_invite_link = config.HELP_ADMIN # Error hone par support link do
                    err_msg = f"❌ <b>Bot Permission Error!</b>\n\nBot is not admin in FSub channel <b>{f['title']}</b> or don't have 'Invite Users' permission."
                else:
                    err_text = str(e)
                    if "NotJoined" in err_text or "user not found" in err_text.lower():
                        err_msg = f"👋 <b>Wait!</b>\n\nResults dekhne ke liye pehle hamara channel <b>{f['title']}</b> join karein.\n\nJoin karne ke baad dobara search karein!"
                    else:
                        err_msg = f"❌ <b>FSub Error!</b>\n<code>{err_text}</code>"

                btn_txt = "✨ Rᴇǫᴜᴇsᴛ Tᴏ Jᴏɪɴ ✨" if is_req else "✨ Jᴏɪɴ Cʜᴀɴɴᴇʟ ✨"
                markup.add(types.InlineKeyboardButton(btn_txt, url=fsub_invite_link))
                markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))
                
                return bot.reply_to(message, err_msg, reply_markup=markup, parse_mode='HTML')

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
        return

    # Suggestions Logic (Removing duplicates)
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
        bot.send_message(target_chat, f"❌ <b>Post missing!</b>\nDatabase channel se delete ho gayi hai.", reply_to_message_id=r_mid)

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
