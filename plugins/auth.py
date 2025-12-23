from bot_instance import bot
import database as db
import config
from telebot import types

@bot.my_chat_member_handler()
def handle_membership_security(message):
    new = message.new_chat_member
    chat = message.chat
    inviter_id = message.from_user.id # Jisne bot ko add/change kiya

    # --- CHANNEL PROTECTION ---
    if chat.type == "channel":
        # Agar bot channel mein Administrator ya Member banaya gaya hai
        if new.status in ["administrator", "member"]:
            # Check permission: Kya add karne wala Admin ya Owner hai?
            if not db.is_admin(inviter_id):
                bot.leave_chat(chat.id)
                print(f"🚫 Unauthorized: Bot left channel '{chat.title}' (Added by {inviter_id})")
            else:
                # Sirf authorized log ke liye PM mein button bhejna
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("➕ Add Filter", callback_data=f"setup|{chat.id}|{chat.title}")
                )
                try:
                    bot.send_message(
                        config.OWNER_ID, 
                        f"📢 <b>Channel Authorized!</b>\n\nChannel: {chat.title}\nID: <code>{chat.id}</code>\nAdded by: <code>{inviter_id}</code>", 
                        reply_markup=markup
                    )
                except:
                    pass

    # --- GROUP TRACKING (For /gbroadcast) ---
    elif chat.type in ["group", "supergroup"]:
        if new.status in ["administrator", "member"]:
            db.add_group(chat.id, chat.title)
            # Group mein welcome msg (Optional)
            if new.status == "member":
                bot.send_message(chat.id, "👋 <b>Hello Everyone!</b>\nAnime search karne ke liye anime ka naam likhein.")
        elif new_status in ["left", "kicked"]:
            db.remove_group(chat.id)

# Groups mein naye members detect karne ke liye (Double check)
@bot.message_handler(content_types=['new_chat_members'])
def on_join_group(message):
    for user in message.new_chat_members:
        if user.id == bot.get_me().id:
            db.add_group(message.chat.id, message.chat.title)
