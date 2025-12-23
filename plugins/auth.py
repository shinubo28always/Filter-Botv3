from bot_instance import bot
import database as db
import config
from telebot import types

@bot.my_chat_member_handler()
def handle_membership_security(message):
    new = message.new_chat_member
    chat = message.chat
    
    # User ID nikalna jisne status change kiya
    inviter_id = message.from_user.id 

    # --- CHANNEL LOGIC ---
    if chat.type == "channel":
        # Jab bot Administrator banaya jaye
        if new.status == "administrator":
            # Check permission: Kya add karne wala Admin ya Owner hai?
            if db.is_admin(inviter_id):
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("➕ Add Filter", callback_data=f"setup|{chat.id}|{chat.title}")
                )
                try:
                    # PM mein setup msg bhejrein
                    bot.send_message(
                        inviter_id, 
                        f"✅ <b>Channel Authorized!</b>\n\nChannel: <b>{chat.title}</b>\nID: <code>{chat.id}</code>\n\nAb aap niche button par click karke filter setup kar sakte hain.", 
                        reply_markup=markup
                    )
                    print(f"✅ PM Sent to {inviter_id} for channel {chat.title}")
                except Exception as e:
                    # Agar user ne bot start nahi kiya toh Owner ko batao
                    bot.send_message(config.OWNER_ID, f"⚠️ <b>Setup Warning!</b>\nAdmin <code>{inviter_id}</code> ne bot ko channel mein add kiya par unka PM block hai.\n\nChannel: {chat.title}")
            else:
                # Unauthorized user: Auto Leave
                bot.leave_chat(chat.id)
                print(f"🚫 Unauthorized leave from: {chat.title}")

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
            bot.send_message(message.chat.id, "👋 <b>Hello Everyone!</b>\nAnime search karne ke liye anime ka naam likhein.")
