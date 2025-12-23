from bot_instance import bot
import database as db
import config
from telebot import types

@bot.my_chat_member_handler()
def handle_membership_security(message):
    new = message.new_chat_member
    chat = message.chat
    inviter_id = message.from_user.id 

    # --- CHANNEL PROTECTION (Strict) ---
    if chat.type == "channel":
        if new.status in ["administrator", "member"]:
            if not db.is_admin(inviter_id):
                bot.leave_chat(chat.id)
            else:
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("➕ Add Filter", callback_data=f"setup|{chat.id}|{chat.title}")
                )
                bot.send_message(config.OWNER_ID, f"📢 <b>Channel Authorized!</b>\n\nChannel: {chat.title}", reply_markup=markup)

    # --- GROUP TRACKING (Public/Private Groups) ---
    elif chat.type in ["group", "supergroup"]:
        if new.status in ["administrator", "member"]:
            db.add_group(chat.id, chat.title)
            print(f"✅ Group {chat.title} ({chat.id}) added to DB.")
        elif new.status in ["left", "kicked"]:
            db.del_group(chat.id)

# Groups mein naye members detect karne ke liye
@bot.message_handler(content_types=['new_chat_members'])
def on_join_group(message):
    for user in message.new_chat_members:
        if user.id == bot.get_me().id:
            db.add_group(message.chat.id, message.chat.title)
            bot.send_message(message.chat.id, "👋 <b>Hello! I am alive.</b>\nSearch anime by typing its name!")
