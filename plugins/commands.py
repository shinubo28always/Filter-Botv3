from bot_instance import bot
import config
import database as db
from telebot import types
import time

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_sticker(message.chat.id, config.STICKER_ID)
    time.sleep(1)
    txt = "🎬 <b>Welcome to Anime Filter Bot!</b>\n\nMain aapke liye anime search kar sakta hoon aur unka data fetch kar sakta hoon.\n\n<b>Usage:</b> Bas anime ka naam likhein!"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Updates", url=config.LINK_ANIME_CHANNEL))
    bot.send_message(message.chat.id, txt, reply_markup=markup, message_effect_id=config.EFFECT_FIRE)

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    start = time.time()
    msg = bot.reply_to(message, "⚡")
    ms = round((time.time() - start) * 1000)
    bot.edit_message_text(f"📶 <b>Pong:</b> <code>{ms}ms</code>", message.chat.id, msg.message_id)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not db.is_admin(message.from_user.id): return
    # MongoDB se count nikalna
    u_count = db.users.count_documents({})
    f_count = db.filters.count_documents({})
    bot.reply_to(message, f"📊 <b>Bot Stats:</b>\n\n👥 Users: <code>{u_count}</code>\n📂 Filters: <code>{f_count}</code>")

@bot.message_handler(commands=['add_admin'])
def add_admin_cmd(message):
    if str(message.from_user.id) != str(config.OWNER_ID): return
    try:
        new_id = message.text.split()[1]
        db.admins.update_one({"_id": str(new_id)}, {"$set": {"_id": str(new_id)}}, upsert=True)
        bot.reply_to(message, f"✅ User <code>{new_id}</code> is now an Admin.")
    except:
        bot.reply_to(message, "Usage: /add_admin USER_ID")

@bot.message_handler(commands=['reply'])
def reply_cmd(message):
    if not db.is_admin(message.from_user.id): return
    try:
        parts = message.text.split(maxsplit=2)
        target_id = parts[1]
        text = parts[2]
        bot.send_message(target_id, f"<blockquote><b>Message from Admin:</b>\n\n{text}</blockquote>", message_effect_id=config.EFFECT_PARTY)
        bot.reply_to(message, "✅ Replied Successfully.")
    except:
        bot.reply_to(message, "Usage: /reply USER_ID Message")
