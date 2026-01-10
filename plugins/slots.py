### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
from bot_instance import bot
from telebot import types
import database as db
import config

@bot.message_handler(commands=['add_slot'])
def add_slot_handler(message):
    if not db.is_admin(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/add_slot keyword</code>")
    
    keyword = parts[1].lower().strip()
    markup = types.ForceReply(selective=True)
    msg = bot.reply_to(message, f"📥 <b>Manual Slot Setup</b>\nKeyword: <code>{keyword}</code>\n\nAb wo <b>Message (Text/Media)</b> bhejein jo aap set karna chahte hain:", reply_markup=markup)
    bot.register_next_step_handler(msg, save_slot_content, keyword)

def save_slot_content(message, keyword):
    try:
        db_msg = bot.copy_message(config.DB_CHANNEL_ID, message.chat.id, message.message_id)
        data = {
            "title": f"Manual: {keyword.title()}",
            "db_mid": db_msg.message_id,
            "type": "slot"
        }
        db.add_filter(keyword, data)
        bot.reply_to(message, f"✅ <b>Slot Added!</b>\nKeyword: <code>{keyword}</code>")
    except Exception as e:
        bot.reply_to(message, f"❌ <b>Error!</b>\n<code>{str(e)}</code>")
