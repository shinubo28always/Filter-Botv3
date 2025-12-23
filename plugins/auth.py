import html
from bot_instance import bot
import database as db
import config
from telebot import types

@bot.my_chat_member_handler()
def handle_membership_security(message):
    new = message.new_chat_member
    chat = message.chat
    
    # Inviter detect karna
    inviter_id = message.from_user.id if message.from_user else None

    # --- CHANNEL PROTECTION ---
    if chat.type == "channel":
        if new.status == "administrator":
            # Security Check
            if inviter_id and db.is_admin(inviter_id):
                # Channel title ko clean karna
                safe_title = html.escape(chat.title)
                
                # IMPORTANT: Callback data mein sirf ID bhej rahe hain (limit check ke liye)
                # Format: setup|chat_id
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("➕ Add Filter", callback_data=f"setup|{chat.id}")
                )
                
                txt = (
                    f"✅ <b>Channel Authorized!</b>\n\n"
                    f"Channel: <b>{safe_title}</b>\n"
                    f"ID: <code>{chat.id}</code>\n\n"
                    f"Aap niche button se is channel ke anime filters add kar sakte hain."
                )
                
                try:
                    bot.send_message(inviter_id, txt, reply_markup=markup, parse_mode='HTML')
                except:
                    # Fallback to Owner
                    try:
                        bot.send_message(
                            config.OWNER_ID, 
                            f"📢 <b>Authorized:</b> {safe_title}\nID: <code>{chat.id}</code>", 
                            reply_markup=markup, 
                            parse_mode='HTML'
                        )
                    except: pass
            else:
                # Unauthorized user: Leave
                try: bot.leave_chat(chat.id)
                except: pass

    # --- GROUP TRACKING ---
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
            bot.send_message(message.chat.id, "👋 <b>Bot Active!</b>\nType anime name to search.")
