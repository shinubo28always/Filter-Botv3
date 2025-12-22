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
    bot.send_message(message.chat.id, "🎬 <b>Welcome!</b>\nType anime name to search.", reply_markup=markup, message_effect_id=config.EFFECT_FIRE)

@bot.message_handler(commands=['filters'])
def list_filters(message):
    if not db.is_admin(message.from_user.id): return
    fs = db.get_all_filters_list()
    if not fs: return bot.reply_to(message, "Empty.")
    txt = "📂 <b>Filters:</b>\n" + "\n".join([f"• <code>{x['keyword']}</code>" for x in fs])
    bot.reply_to(message, txt[:4000])

@bot.message_handler(commands=['del_filter'])
def del_filter(message):
    if not db.is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Usage: /del_filter name/all")
    target = args[1].lower()
    if target == "all":
        if db.get_filter("all"): db.delete_filter("all")
        else:
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("Confirm Delete All", callback_data="conf_del_all"))
            return bot.reply_to(message, "⚠️ Delete all filters?", reply_markup=markup)
    elif db.delete_filter(target): bot.reply_to(message, f"Deleted {target}")
    else: bot.reply_to(message, "Not found.")

@bot.callback_query_handler(func=lambda call: call.data == "conf_del_all")
def conf_del(call):
    db.delete_all_filters()
    bot.edit_message_text("🗑 All filters deleted.", call.message.chat.id, call.message.message_id)
