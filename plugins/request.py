from bot_instance import bot
import config
import database as db
from telebot import types

@bot.message_handler(commands=['request'])
def request_handler(message):
    query = message.text.replace("/request", "").strip()
    if not query:
        return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/request Naruto Shippuden</code>")
    
    uid = message.from_user.id
    name = message.from_user.first_name
    db.save_request(uid, name, query)
    
    # Notify Admin
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("Reply", callback_data=f"rep|{uid}")
    )
    admin_msg = f"📩 <b>New Request!</b>\n\n👤 From: {name} (<code>{uid}</code>)\n📝 Anime: <code>{query}</code>"
    bot.send_message(config.OWNER_ID, admin_msg, reply_markup=markup)
    
    bot.reply_to(message, "✅ <b>Request Sent!</b> Admin will notify you soon.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("rep|"))
def reply_callback(call):
    target_id = call.data.split("|")[1]
    msg = bot.send_message(call.from_user.id, f"📝 Send your reply for <code>{target_id}</code>:")
    bot.register_next_step_handler(msg, send_reply_to_user, target_id)

def send_reply_to_user(message, target_id):
    try:
        bot.send_message(target_id, f"<blockquote><b>Admin Reply:</b>\n\n{message.text}</blockquote>", message_effect_id=config.EFFECT_PARTY)
        bot.reply_to(message, "✅ Reply Delivered!")
    except: bot.reply_to(message, "❌ Failed (User blocked bot).")
