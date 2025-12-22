from bot_instance import bot
import database as db
import time

@bot.message_handler(commands=['broadcast'])
def broadcast_handler(message):
    if not db.is_admin(message.from_user.id): return
    msg_to_send = message.reply_to_message
    if not msg_to_send:
        return bot.reply_to(message, "⚠️ Reply to a message to broadcast.")
    
    users = db.get_all_users()
    total = len(users)
    count = 0
    status = bot.reply_to(message, f"🚀 <b>Starting Broadcast...</b>\nTotal: {total}")
    
    for uid in users:
        try:
            bot.copy_message(uid, message.chat.id, msg_to_send.message_id)
            count += 1
            if count % 50 == 0:
                bot.edit_message_text(f"⏳ <b>Sending...</b>\nProgress: {count}/{total}", message.chat.id, status.message_id)
        except: pass
    
    bot.edit_message_text(f"✅ <b>Broadcast Complete!</b>\nDelivered to: {count} users.", message.chat.id, status.message_id)
