from bot_instance import bot
import config, database as db, time
from telebot import types

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_sticker(m.chat.id, config.STICKER_ID)
    bot.send_message(m.chat.id, "🎬 <b>Bot Alive!</b>", message_effect_id=config.EFFECT_FIRE)

@bot.message_handler(commands=['ping'])
def ping(m):
    s = time.time()
    msg = bot.reply_to(m, "📶")
    bot.edit_message_text(f"🚀 {round((time.time()-s)*1000)}ms", m.chat.id, msg.message_id)

@bot.message_handler(commands=['stats'])
def stats(m):
    if not db.is_admin(m.from_user.id): return
    u, f = len(db.get_all_users()), len(db.get_all_filters_list())
    bot.reply_to(m, f"📊 <b>Stats:</b>\nUsers: {u}\nFilters: {f}")

@bot.message_handler(commands=['filters'])
def list_f(m):
    if not db.is_admin(m.from_user.id): return
    fs = db.get_all_filters_list()
    txt = "📂 <b>Filters:</b>\n" + "\n".join([f"• <code>{x['keyword']}</code>" for x in fs])
    bot.reply_to(m, txt[:4000])

@bot.message_handler(commands=['del_filter'])
def del_f(m):
    if not db.is_admin(m.from_user.id): return
    try:
        t = m.text.split()[1].lower()
        if t == "all":
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Confirm All", callback_data="conf_all"))
            return bot.reply_to(m, "⚠️ Delete All?", reply_markup=markup)
        if db.delete_filter(t): bot.reply_to(m, "Deleted.")
        else: bot.reply_to(m, "Not found.")
    except: pass

@bot.callback_query_handler(func=lambda c: c.data == "conf_all")
def conf_all(c):
    db.delete_all_filters(); bot.edit_message_text("🗑 All Deleted.", c.message.chat.id, c.message.message_id)
