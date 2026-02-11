# --- Support: @DogeshBhai_Pure_Bot | Dev: @AniReal_Support ---
from bot_instance import bot
import database as db
from telebot import types
import config
import time

# --- UTILS: ADMIN CHECK ---
def check_admin(message):
    if not db.is_admin(message.from_user.id):
        bot.reply_to(message, "❌ **You are not authorized!**")
        return False
    return True

# --- 1. ADD FSUB ---
@bot.message_handler(commands=['add_fsub'])
def add_fsub_start(message):
    if not check_admin(message): return
    try:
        args = message.text.split()
        if len(args) < 2: 
            return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/add_fsub -100xxxx</code>", parse_mode="HTML")
        
        target_id = args[1]
        chat = bot.get_chat(target_id) # Bot must be admin in that channel
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🔴 Normal", callback_data=f"fsub_init|normal|{target_id}|{chat.title}"),
            types.InlineKeyboardButton("🟢 Request", callback_data=f"fsub_init|request|{target_id}|{chat.title}")
        )
        bot.reply_to(message, f"⚙️ <b>Select Mode for:</b>\n{chat.title}", reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        bot.reply_to(message, f"❌ <b>Error:</b>\n<code>{e}</code>", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fsub_init|"))
def save_new_fsub(call):
    bot.answer_callback_query(call.id, "Adding...")
    _, mode, cid, title = call.data.split("|")
    db.add_fsub_chnl(cid, title, mode)
    
    emoji = "🔴 Normal" if mode == "normal" else "🟢 Request"
    bot.edit_message_text(
        f"✅ <b>FSub Added Successfully!</b>\n\nChannel: <b>{title}</b>\nMode: <b>{emoji}</b>", 
        call.message.chat.id, call.message.message_id, parse_mode="HTML"
    )

# --- 2. FSUB LIST ---
@bot.message_handler(commands=['fsub'])
def list_fsub_handler(message):
    if not check_admin(message): return
    send_main_menu(message.chat.id)

def send_main_menu(chat_id, edit_mid=None):
    chnls = db.get_all_fsub()
    if not chnls:
        txt = "📂 <b>No FSub Channels found.</b>"
        if edit_mid: bot.edit_message_text(txt, chat_id, edit_mid, parse_mode="HTML")
        else: bot.send_message(chat_id, txt, parse_mode="HTML")
        return

    markup = types.InlineKeyboardMarkup()
    for c in chnls:
        # DB structure ke hisaab se c['_id'] ya c['cid'] check karein
        cid = c.get('_id', c.get('cid'))
        emoji = "🟢" if c.get('mode') == "request" else "🔴"
        markup.add(types.InlineKeyboardButton(f"{emoji} {c['title']}", callback_data=f"fsub_manage|{cid}"))
    
    txt = "📢 <b>FSub Management List:</b>\nClick a channel to change mode or delete."
    if edit_mid: 
        bot.edit_message_text(txt, chat_id, edit_mid, reply_markup=markup, parse_mode="HTML")
    else: 
        bot.send_message(chat_id, txt, reply_markup=markup, parse_mode="HTML")

# --- 3. MANAGE CHANNEL ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("fsub_manage|"))
def manage_channel_ui(call):
    bot.answer_callback_query(call.id)
    cid = call.data.split("|")[1]
    info = db.get_fsub_info(cid)
    
    if not info:
        return bot.answer_callback_query(call.id, "❌ Channel not found in DB", show_alert=True)
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🔴 Normal", callback_data=f"fsub_upd|normal|{cid}"),
        types.InlineKeyboardButton("🟢 Request", callback_data=f"fsub_upd|request|{cid}")
    )
    markup.add(types.InlineKeyboardButton("🗑️ Remove Channel", callback_data=f"fsub_del_single|{cid}"))
    markup.add(types.InlineKeyboardButton("⬅️ Back to List", callback_data="fsub_back"))
    
    curr_mode = "🔴 Normal" if info.get('mode') == "normal" else "🟢 Request"
    txt = f"⚙️ <b>Manage Channel:</b>\n\nName: <b>{info['title']}</b>\nID: <code>{cid}</code>\nMode: <b>{curr_mode}</b>\n\nChoose new mode below:"
    bot.edit_message_text(txt, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fsub_upd|"))
def update_mode_callback(call):
    _, mode, cid = call.data.split("|")
    db.update_fsub_mode(cid, mode)
    
    emoji = "🔴 Normal" if mode == "normal" else "🟢 Request"
    bot.answer_callback_query(call.id, f"✅ Switched to {emoji}")
    
    # Bina sleep ke seedha refresh karein (behtar UX)
    send_main_menu(call.message.chat.id, edit_mid=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "fsub_back")
def back_to_fsub_list(call):
    bot.answer_callback_query(call.id)
    send_main_menu(call.message.chat.id, edit_mid=call.message.message_id)

# --- 4. DELETE LOGIC ---
@bot.message_handler(commands=['del_fsub'])
def del_fsub_handler(message):
    if not check_admin(message): return
    args = message.text.split()
    
    if len(args) < 2: 
        return bot.reply_to(message, "⚠️ <b>Usage:</b>\n<code>/del_fsub ID</code>\n<code>/del_fsub all</code>", parse_mode="HTML")
    
    target = args[1].lower()
    if target == "all":
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ Confirm Delete All", callback_data="fsub_del_all"),
            types.InlineKeyboardButton("❌ Cancel", callback_data="fsub_back")
        )
        bot.reply_to(message, "⚠️ <b>Warning:</b> Are you sure you want to delete ALL FSub channels?", reply_markup=markup, parse_mode="HTML")
    else:
        if db.del_fsub_chnl(target):
            bot.reply_to(message, f"🗑️ Channel <code>{target}</code> removed.", parse_mode="HTML")
        else:
            bot.reply_to(message, "❌ Channel not found.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("fsub_del"))
def delete_callbacks(call):
    if call.data == "fsub_del_all":
        db.del_all_fsub_chnls()
        bot.answer_callback_query(call.id, "All Deleted")
        bot.edit_message_text("🗑️ All FSub channels removed successfully.", call.message.chat.id, call.message.message_id)
        
    elif call.data.startswith("fsub_del_single|"):
        cid = call.data.split("|")[1]
        db.del_fsub_chnl(cid)
        bot.answer_callback_query(call.id, "Removed")
        # List refresh karein
        send_main_menu(call.message.chat.id, edit_mid=call.message.message_id)

# Join & Support Us! @DogeshBhai_Pure_Bot
