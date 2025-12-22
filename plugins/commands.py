from bot_instance import bot
import config
import database as db
from telebot import types
import time

@bot.message_handler(commands=['start'])
def start_cmd(message):
    bot.send_sticker(message.chat.id, config.STICKER_ID)
    time.sleep(1)
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📢 Updates", url=config.LINK_ANIME_CHANNEL))
    bot.send_message(message.chat.id, "🎬 <b>Welcome!</b>\nType anime name to search or use /help.", reply_markup=markup, message_effect_id=config.EFFECT_FIRE)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    txt = (
        "📖 <b>Bot Commands:</b>\n\n"
        "• <code>/start</code> - Check bot alive\n"
        "• <code>/ping</code> - Check speed\n"
        "• <code>/request [name]</code> - Request anime\n"
        "• <code>/filters</code> - List all filters (Admin)\n"
        "• <code>/stats</code> - Bot stats (Admin)\n"
        "• <code>/broadcast</code> - Send msg to all (Admin)"
    )
    bot.reply_to(message, txt)

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    start = time.time()
    msg = bot.reply_to(message, "📶")
    ms = round((time.time() - start) * 1000)
    bot.edit_message_text(f"🚀 <b>Speed:</b> <code>{ms}ms</code>", message.chat.id, msg.message_id)

@bot.message_handler(commands=['admins'])
def list_admins_cmd(message):
    if not db.is_admin(message.from_user.id): return
    adms = db.get_all_admins()
    txt = "👮 <b>Admins List:</b>\n\n" + "\n".join([f"• <code>{a}</code>" for a in adms])
    bot.reply_to(message, txt)

@bot.message_handler(commands=['add_admin'])
def add_adm(message):
    if str(message.from_user.id) != str(config.OWNER_ID): return
    try:
        uid = message.text.split()[1]
        db.add_admin(uid)
        bot.reply_to(message, f"✅ Admin Added: <code>{uid}</code>")
    except: bot.reply_to(message, "Usage: /add_admin ID")

@bot.message_handler(commands=['del_admin'])
def del_adm(message):
    if str(message.from_user.id) != str(config.OWNER_ID): return
    try:
        uid = message.text.split()[1]
        db.del_admin(uid)
        bot.reply_to(message, "🗑 Admin Removed.")
    except: bot.reply_to(message, "Usage: /del_admin ID")
