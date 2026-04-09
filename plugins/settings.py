from bot_instance import bot
from telebot import types
import database as db
import config

def get_settings_markup():
    s = db.get_bot_settings()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"Private Expiry: {s['private_expiry']}s", callback_data="set_val|private_expiry", style='primary'))
    markup.add(types.InlineKeyboardButton(f"Public Expiry: {s['public_expiry']}s", callback_data="set_val|public_expiry", style='primary'))
    markup.add(types.InlineKeyboardButton(f"Auto Delete: {s['auto_delete']}s", callback_data="set_val|auto_delete", style='primary'))
    markup.add(types.InlineKeyboardButton(f"Button: {s['button_text']}", callback_data="set_val|button_text", style='primary'))

    theme_display = s['theme'].capitalize()
    markup.add(types.InlineKeyboardButton(f"Theme: {theme_display}", callback_data="set_theme_menu", style='primary'))

    markup.add(types.InlineKeyboardButton("Close", callback_data="close_settings", style='danger'))
    return markup

@bot.message_handler(commands=['settings'])
def settings_panel(message):
    if not db.is_admin(message.from_user.id):
        return bot.reply_to(message, config.ROAST_GENERAL)

    bot.send_message(message.chat.id, "⚙️ <b>Bot Settings Panel</b>\n\nConfigure your bot's behavior from here:", reply_markup=get_settings_markup(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "close_settings")
def close_settings(call):
    if not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "❌ Not for you!")
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("set_val|"))
def set_val_handler(call):
    if not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "❌ Not for you!")

    key = call.data.split("|")[1]
    prompt_text = {
        "private_expiry": "Enter Auto Expiry time for Private Channels (in seconds):",
        "public_expiry": "Enter Auto Expiry time for Public Channels (in seconds):",
        "auto_delete": "Enter Auto Delete time for result messages (in seconds):",
        "button_text": "Enter the text for the result button (e.g. Watch & Download):"
    }.get(key, "Enter new value:")

    msg = bot.send_message(call.message.chat.id, f"📥 <b>{prompt_text}</b>", reply_markup=types.ForceReply(selective=True), parse_mode="HTML")
    bot.register_next_step_handler(msg, process_setting_update, key, call.message.message_id)

def process_setting_update(message, key, panel_mid):
    val = message.text
    if key in ["private_expiry", "public_expiry", "auto_delete"]:
        if not val.isdigit():
            bot.reply_to(message, "❌ Invalid input! Please enter a number.")
            return
        val = int(val)

    db.update_bot_setting(key, val)
    bot.reply_to(message, f"✅ <b>{key.replace('_', ' ').capitalize()}</b> updated successfully!", parse_mode="HTML")

    # Update the panel
    try:
        bot.edit_message_reply_markup(message.chat.id, panel_mid, reply_markup=get_settings_markup())
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == "set_theme_menu")
def theme_menu(call):
    if not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "❌ Not for you!")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Default Style", callback_data="update_theme|default", style='primary'))
    markup.add(types.InlineKeyboardButton("Stylish Bold", callback_data="update_theme|stylish", style='primary'))
    markup.add(types.InlineKeyboardButton("Back", callback_data="back_to_settings", style='success'))

    bot.edit_message_text("🎨 <b>Select Anime Result Theme:</b>\n\nChoose the visual style for new filters:", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("update_theme|"))
def update_theme(call):
    if not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "❌ Not for you!")

    theme = call.data.split("|")[1]
    db.update_bot_setting("theme", theme)
    bot.answer_callback_query(call.id, f"✅ Theme set to {theme}!")
    back_to_settings(call)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_settings")
def back_to_settings(call):
    if not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "❌ Not for you!")

    bot.edit_message_text("⚙️ <b>Bot Settings Panel</b>\n\nConfigure your bot's behavior from here:", call.message.chat.id, call.message.message_id, reply_markup=get_settings_markup(), parse_mode="HTML")
