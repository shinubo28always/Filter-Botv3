import html
from bot_instance import bot
import database as db
import config
from telebot import types

@bot.my_chat_member_handler()
def handle_membership_security(message):
    new = message.new_chat_member
    chat = message.chat
    
    # Kisne bot ko add kiya (Inviter ID)
    inviter_id = message.from_user.id if message.from_user else None

    # --- CHANNEL PROTECTION ---
    if chat.type == "channel":
        # Jab bot Administrator banaya jaye
        if new.status == "administrator":
            # Check permission: Kya add karne wala Admin ya Owner hai?
            if inviter_id and db.is_admin(inviter_id):
                safe_title = html.escape(chat.title)
                
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("➕ Add Filter", callback_data=f"setup|{chat.id}|{safe_title}")
                )
                
                txt = (
                    f"✅ <b>Channel Authorized!</b>\n\n"
                    f"Channel: <b>{safe_title}</b>\n"
                    f"ID: <code>{chat.id}</code>\n\n"
                    f"Aap niche button se is channel ke anime filters add kar sakte hain."
                )
                
                try:
                    # Pehle inviter ko bhejte hain (Jisne add kiya)
                    bot.send_message(inviter_id, txt, reply_markup=markup, parse_mode='HTML')
                except:
                    # Fallback: Agar inviter ko nahi gaya, toh Main Owner ko bhejte hain
                    try:
                        bot.send_message(
                            config.OWNER_ID, 
                            f"📢 <b>Channel Authorized by Admin {inviter_id}:</b>\n{safe_title}", 
                            reply_markup=markup, 
                            parse_mode='HTML'
                        )
                    except: pass
            else:
                # Unauthorized user: Auto Leave
                try: bot.leave_chat(chat.id)
                except: pass

    # --- GROUP LOGIC ---
    elif chat.type in ["group", "supergroup"]:
        if new.status in ["administrator", "member"]:
            db.add_group(chat.id, chat.title)
        elif new.status in ["left", "kicked"]:
            db.del_group(chat.id)

@bot.message_handler(content_types=['new_chat_members'])
def on_join_group(message):
    for user in message.new_chat_members:
        if user.id == bot.get_me().id:
            db.add_group(message.chat.id, message.chat.title)
            bot.send_message(message.chat.id, "👋 <b>Hello Everyone!</b>\nAnime dhundne ke liye anime ka naam likhein.")
