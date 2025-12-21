from bot_instance import bot
import database as db
import config
from telebot import types

@bot.my_chat_member_handler()
def handle_auth(message):
    new_status = message.new_chat_member.status
    uid = message.from_user.id
    if message.chat.type == "channel" and new_status in ['administrator', 'member']:
        if not db.is_admin(uid):
            bot.leave_chat(message.chat.id)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("➕ Add Filter", callback_data=f"setup|{message.chat.id}|{message.chat.title}"))
            bot.send_message(config.OWNER_ID, f"📢 <b>Authorized:</b> {message.chat.title}", reply_markup=markup)
