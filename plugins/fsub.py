from bot_instance import bot
import database as db
from telebot import types
import config

# --- 1. ADD FSUB: SELECT MODE FIRST ---
@bot.message_handler(commands=['add_fsub'])
def add_fsub_start(message):
    if not db.is_admin(message.from_user.id): return
    try:
        args = message.text.split()
        if len(args) < 2: 
            return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/add_fsub -100xxxx</code>")
        
        target_id = args[1]
        chat = bot.get_chat(target_id)
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🔴 Normal", callback_data=f"fsub_init|normal|{target_id}|{chat.title}"),
            types.InlineKeyboardButton("🟢 Request", callback_data=f"fsub_init|request|{target_id}|{chat.title}")
        )
        bot.reply_to(message, f"⚙️ <b>Select Mode for:</b>\n{chat.title}", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"❌ <b>Error:</b> Bot admin nahi hai ya ID galat hai.\nDetails: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fsub_init|"))
def save_new_fsub(call):
    _, mode, cid, title = call.data.split("|")
    db.add_fsub_chnl(cid, title, mode)
    emoji = "🔴 Normal" if mode == "normal" else "🟢 Request"
    bot.edit_message_text(f"✅ <b>FSub Added Successfully!</b>\n\nChannel: <b>{title}</b>\nMode: <b>{emoji}</b>", call.message.chat.id, call.message.message_id)

# --- 2. FSUB LIST: SINGLE BUTTON STYLE ---
@bot.message_handler(commands=['fsub'])
def list_fsub_handler(message):
    if not db.is_admin(message.from_user.id): return
    send_main_menu(message.chat.id)

def send_main_menu(chat_id, edit_mid=None):
    chnls = db.get_all_fsub()
    if not chnls:
        txt = "📂 <b>No FSub Channels found.</b>"
        if edit_mid: bot.edit_message_text(txt, chat_id, edit_mid)
        else: bot.send_message(chat_id, txt)
        return

    markup = types.InlineKeyboardMarkup()
    for c in chnls:
        emoji = "🟢" if c['mode'] == "request" else "🔴"
        markup.add(types.InlineKeyboardButton(f"{emoji} {c['title']}", callback_data=f"fsub_manage|{c['_id']}"))
    
    txt = "📢 <b>FSub Management List:</b>\nClick a channel to change mode or delete."
    if edit_mid: bot.edit_message_text(txt, chat_id, edit_mid, reply_markup=markup)
    else: bot.send_message(chat_id, txt, reply_markup=markup)

# --- 3. MANAGE CHANNEL: CHANGE MODE OR DELETE ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("fsub_manage|"))
def manage_channel_ui(call):
    cid = call.data.split("|")[1]
    info = db.get_fsub_info(cid)
    if not info: return
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🔴 Normal", callback_data=f"fsub_upd|normal|{cid}"),
        types.InlineKeyboardButton("🟢 Request", callback_data=f"fsub_upd|request|{cid}")
    )
    markup.add(types.InlineKeyboardButton("🗑️ Remove Channel", callback_data=f"fsub_del_single|{cid}"))
    markup.add(types.InlineKeyboardButton("⬅️ Back to List", callback_data="fsub_back"))
    
    curr_mode = "🔴 Normal (2m)" if info['mode'] == "normal" else "🟢 Request (5m)"
    txt = f"⚙️ <b>Manage Channel:</b>\n\nName: <b>{info['title']}</b>\nID: <code>{cid}</code>\nMode: <b>{curr_mode}</b>\n\nChoose new mode below:"
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fsub_upd|"))
def update_mode_callback(call):
    _, mode, cid = call.data.split("|")
    db.update_fsub_mode(cid, mode)
    emoji = "🔴 Normal" if mode == "normal" else "🟢 Request"
    
    # Edit message to show success
    bot.edit_message_text(f"✅ <b>{emoji} successfully done!</b>", call.message.chat.id, call.message.message_id)
    # Refresh list after 2 seconds
    import time
    time.sleep(1.5)
    send_main_menu(call.message.chat.id, edit_mid=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "fsub_back")
def back_to_fsub_list(call):
    send_main_menu(call.message.chat.id, edit_mid=call.message.message_id)

# --- 4. DELETE ALL LOGIC ---
@bot.message_handler(commands=['del_fsub'])
def del_fsub_handler(message):
    if not db.is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: /del_fsub ID or all")
    
    target = args[1].lower()
    if target == "all":
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ Confirm All Delete", callback_data="fsub_del_all"),
            types.InlineKeyboardButton("❌ Cancel", callback_data="fsub_back")
        )
        bot.reply_to(message, "⚠️ <b>Warning:</b> Delete all FSub channels?", reply_markup=markup)
    else:
        if db.del_fsub_chnl(target): bot.reply_to(message, "🗑️ Removed.")
        else: bot.reply_to(message, "❌ Not found.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fsub_del"))
def delete_callbacks(call):
    if call.data == "fsub_del_all":
        db.del_all_fsub_chnls()
        bot.edit_message_text("🗑️ All FSub channels removed.", call.message.chat.id, call.message.message_id)
    elif call.data.startswith("fsub_del_single|"):
        cid = call.data.split("|")[1]
        db.del_fsub_chnl(cid)
        bot.edit_message_text("🗑️ Channel removed successfully.", call.message.chat.id, call.message.message_id)
        import time
        time.sleep(1.5)
        send_main_menu(call.message.chat.id, edit_mid=call.message.message_id)
