from bot_instance import bot
import config
import database as db
from telebot import types
import time

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_sticker(message.chat.id, config.STICKER_ID)
    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("📢 Updates", url=config.LINK_ANIME_CHANNEL))
    bot.send_message(message.chat.id, "🎬 <b>Bot Online!</b>\nSearch anime below.", reply_markup=markup, message_effect_id=config.EFFECT_FIRE)

@bot.message_handler(commands=['filters'])
def list_fs(message):
    if not db.is_admin(message.from_user.id): return
    fs = db.get_all_filters_list()
    if not fs: return bot.reply_to(message, "No filters.")
    txt = "📂 <b>Filters:</b>\n" + "\n".join([f"• <code>{x['keyword']}</code>" for x in fs])
    bot.reply_to(message, txt[:4000])

@bot.message_handler(commands=['del_filter'])
def delete_fs(message):
    if not db.is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "Usage: /del_filter name/all")
    
    target = args[1].lower()
    if target == "all":
        if db.get_filter("all"): 
            db.delete_filter("all")
            bot.reply_to(message, "Deleted filter named 'all'.")
        else:
            markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("Confirm Delete All", callback_data="conf_all"),
                types.InlineKeyboardButton("Cancel", callback_data="cancel")
            )
            bot.reply_to(message, "⚠️ <b>Warning:</b> Delete EVERYTHING?", reply_markup=markup)
    else:
        if db.delete_filter(target): bot.reply_to(message, f"Deleted {target}")
        else: bot.reply_to(message, "Not found.")

@bot.callback_query_handler(func=lambda call: call.data in ["conf_all", "cancel"])
def handle_del_all(call):
    if call.data == "conf_all":
        db.delete_all_filters()
        bot.edit_message_text("🗑 All filters cleared.", call.message.chat.id, call.message.message_id)
    else: bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(commands=['stats'])
def stats(message):
    if not db.is_admin(message.from_user.id): return
    u = len(db.get_all_users())
    f = len(db.get_all_filters_list())
    bot.reply_to(message, f"📊 <b>Stats:</b>\nUsers: {u}\nFilters: {f}")
