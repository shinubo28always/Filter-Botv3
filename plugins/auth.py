from bot_instance import bot
import database as db
import config
from telebot import types

@bot.my_chat_member_handler()
def handle_membership_security(message):
    new = message.new_chat_member
    chat = message.chat
    
    # Inviter ID detect karna
    inviter_id = message.from_user.id if message.from_user else None

    # --- CHANNEL LOGIC (STRICT) ---
    if chat.type == "channel":
        if new.status == "administrator":
            # Check permission: Kya add karne wala Admin/Owner hai?
            if inviter_id and db.is_admin(inviter_id):
                # SUCCESS: PM Notification with setup button
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("➕ Add Filter", callback_data=f"setup|{chat.id}|{chat.title}")
                )
                txt = (
                    f"✅ <b>Channel Authorized!</b>\n\n"
                    f"Channel: <b>{chat.title}</b>\n"
                    f"ID: <code>{chat.id}</code>\n\n"
                    f"Aap niche button se is channel ke anime filters add kar sakte hain."
                )
                try:
                    bot.send_message(inviter_id, txt, reply_markup=markup)
                except:
                    # Agar inviter ko PM nahi ja raha, toh Owner ko alert bhejein
                    bot.send_message(config.OWNER_ID, f"📢 <b>Authorized (via Admin {inviter_id}):</b>\n{chat.title}", reply_markup=markup)
            else:
                # UNAUTHORIZED: Bina msg leave karein
                bot.leave_chat(chat.id)

    # --- GROUP LOGIC (PUBLIC/PRIVATE) ---
    elif chat.type in ["group", "supergroup"]:
        # Jab bot group mein add ho
        if new.status in ["administrator", "member"]:
            db.add_group(chat.id, chat.title)
        # Jab bot group se nikala jaye
        elif new.status in ["left", "kicked"]:
            db.del_group(chat.id)

@bot.message_handler(content_types=['new_chat_members'])
def on_join_group(message):
    """Backup handler for groups where bot is added as member"""
    for user in message.new_chat_members:
        if user.id == bot.get_me().id:
            db.add_group(message.chat.id, message.chat.title)
            # Greeting msg for public groups
            bot.send_message(message.chat.id, "👋 <b>Hello Everyone!</b>\nAnime dhundne ke liye anime ka naam likhein.")
