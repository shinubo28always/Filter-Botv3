from bot_instance import bot
import database as db
from telebot import types
import config

# --- LIST FSUB CHANNELS ---
@bot.message_handler(commands=['fsub'])
def list_fsub_handler(message):
    if not db.is_admin(message.from_user.id): return
    send_fsub_menu(message.chat.id)

def send_fsub_menu(chat_id, edit_mid=None):
    chnls = db.get_all_fsub()
    if not chnls:
        txt = "📂 <b>No FSub Channels added yet.</b>"
        if edit_mid: bot.edit_message_text(txt, chat_id, edit_mid)
        else: bot.send_message(chat_id, txt)
        return

    markup = types.InlineKeyboardMarkup()
    txt = "📢 <b>FSub Management:</b>\n\n🔴 = Normal Mode (2m)\n🟢 = Request Mode (5m)\n\nClick emoji to toggle:"
    
    for c in chnls:
        emoji = "🟢" if c['mode'] == "request" else "🔴"
        markup.add(
            types.InlineKeyboardButton(f"{c['title']}", callback_data="none"),
            types.InlineKeyboardButton(emoji, callback_data=f"toggle_fsub|{c['_id']}")
        )
    
    if edit_mid: bot.edit_message_text(txt, chat_id, edit_mid, reply_markup=markup)
    else: bot.send_message(chat_id, txt, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_fsub|"))
def toggle_fsub_callback(call):
    cid = call.data.split("|")[1]
    db.toggle_fsub_mode(cid)
    send_fsub_menu(call.message.chat.id, edit_mid=call.message.message_id)

# --- ADD & DELETE FSUB ---
@bot.message_handler(commands=['add_fsub'])
def add_fsub_cmd(message):
    if not db.is_admin(message.from_user.id): return
    try:
        args = message.text.split()
        if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: /add_fsub -100xxxx")
        target_id = args[1]
        chat = bot.get_chat(target_id)
        db.add_fsub_chnl(target_id, chat.title)
        bot.reply_to(message, f"✅ <b>FSub Added!</b>\n{chat.title}\nMode: Normal (🔴)")
    exceptException as e:
        bot.reply_to(message, f"❌ Error: ID galat hai ya bot admin nahi hai.\n{e}")

@bot.message_handler(commands=['del_fsub'])
def del_fsub_cmd(message):
    if not db.is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: /del_fsub ID ya all")
    
    target = args[1].lower()
    if target == "all":
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ Confirm All Delete", callback_data="conf_fsub_all"),
            types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_fsub_del")
        )
        bot.reply_to(message, "⚠️ <b>Warning:</b> Delete all FSub channels?", reply_markup=markup)
    else:
        if db.del_fsub_chnl(target): bot.reply_to(message, "🗑️ Deleted.")
        else: bot.reply_to(message, "❌ Not found.")

@bot.callback_query_handler(func=lambda call: call.data in ["conf_fsub_all", "cancel_fsub_del"])
def fsub_del_callback(call):
    if call.data == "conf_fsub_all":
        db.del_all_fsub_chnls()
        bot.edit_message_text("🗑️ All FSub channels removed.", call.message.chat.id, call.message.message_id)
    else: bot.delete_message(call.message.chat.id, call.message.message_id)
