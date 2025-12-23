from bot_instance import bot
import database as db
import config
from telebot import types

@bot.my_chat_member_handler()
def handle_auth(message):
    new_status = message.new_chat_member.status
    chat_type = message.chat.type
    user_id = message.from_user.id

    if chat_type == "channel":
        if new_status in ['administrator', 'member']:
            if not db.is_admin(user_id):
                bot.leave_chat(message.chat.id)
            else:
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("➕ Add Filter", callback_data=f"setup|{message.chat.id}|{message.chat.title}")
                )
                bot.send_message(config.OWNER_ID, f"📢 <b>Authorized:</b> {message.chat.title}", reply_markup=markup)
    
    elif chat_type in ["group", "supergroup"]:
        if new_status in ['administrator', 'member']:
            db.add_group(message.chat.id, message.chat.title)

@bot.message_handler(content_types=['new_chat_members'])
def group_join(message):
    for u in message.new_chat_members:
        if u.id == bot.get_me().id:
            db.add_group(message.chat.id, message.chat.title)
