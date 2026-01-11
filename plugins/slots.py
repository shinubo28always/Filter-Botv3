### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
from bot_instance import bot
from telebot import types
import database as db
import config
import html

# Temporary state tracking
TEMP_SLOTS = {}

def safe_delete(chat_id, msg_id):
    try: bot.delete_message(chat_id, msg_id)
    except: pass

@bot.message_handler(commands=['add_slot'])
def add_slot_start(message):
    if not db.is_admin(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/add_slot keyword</code>")
    
    kw = parts[1].lower().strip()
    uid = message.from_user.id
    
    TEMP_SLOTS[uid] = {
        "kw": kw,
        "buttons": [],
        "curr_name": None,
        "curr_url": None,
        "dash_mid": None, # Dashboard message ID
        "prompt_mid": None # Temporary input prompt ID
    }
    
    markup = types.ForceReply(selective=True)
    msg = bot.reply_to(message, f"📤 <b>Step 1: Content Setup</b>\nKeyword: <code>{kw}</code>\n\n<b>Now send the Message (Text/Media) you want to save</b>:", reply_markup=markup)
    TEMP_SLOTS[uid]['prompt_mid'] = msg.message_id
    bot.register_next_step_handler(msg, process_slot_content)

def process_slot_content(message):
    uid = message.from_user.id
    if uid not in TEMP_SLOTS: return
    
    # Cleanup Step 1
    safe_delete(message.chat.id, TEMP_SLOTS[uid]['prompt_mid'])
    safe_delete(message.chat.id, message.message_id)

    try:
        db_msg = bot.copy_message(config.DB_CHANNEL_ID, message.chat.id, message.message_id)
        TEMP_SLOTS[uid]['db_mid'] = db_msg.message_id
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("➕ Add Custom Buttons", callback_data="slot_add_btn"),
            types.InlineKeyboardButton("⏩ No, Skip This", callback_data="slot_skip")
        )
        
        # Ye hamara Main Dashboard ban jayega
        dash = bot.send_message(uid, "❓ <b>Step 2: Buttons Setup</b>\nDo you want to add custom buttons to this filter?", reply_markup=markup)
        TEMP_SLOTS[uid]['dash_mid'] = dash.message_id
        
    except Exception as e:
        bot.send_message(uid, f"❌ <b>Error:</b> {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("slot_") or call.data.startswith("btn_"))
def handle_slot_callbacks(call):
    uid = call.from_user.id
    if uid not in TEMP_SLOTS:
        return bot.answer_callback_query(call.id, "Session Expired!", show_alert=True)

    if call.data == "slot_skip":
        finalize_slot(call.message, uid)

    elif call.data == "slot_add_btn" or call.data == "btn_refresh":
        refresh_button_menu(call.message, uid)

    elif call.data == "btn_name":
        msg = bot.send_message(uid, "✍️ <b>Send Button Name:</b>", reply_markup=types.ForceReply())
        TEMP_SLOTS[uid]['prompt_mid'] = msg.message_id
        bot.register_next_step_handler(msg, set_btn_name)

    elif call.data == "btn_url":
        msg = bot.send_message(uid, "🌐 <b>Send Button URL:</b>", reply_markup=types.ForceReply())
        TEMP_SLOTS[uid]['prompt_mid'] = msg.message_id
        bot.register_next_step_handler(msg, set_btn_url)

    elif call.data == "btn_add_more":
        data = TEMP_SLOTS[uid]
        if not data['curr_name'] or not data['curr_url']:
            return bot.answer_callback_query(call.id, "❌ Enter Name & URL first!", show_alert=True)
        
        data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        data['curr_name'] = None
        data['curr_url'] = None
        refresh_button_menu(call.message, uid)

    elif call.data == "btn_save":
        data = TEMP_SLOTS[uid]
        if data['curr_name'] and data['curr_url']:
            data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        finalize_slot(call.message, uid)

def refresh_button_menu(message, uid):
    data = TEMP_SLOTS[uid]
    btn_list_txt = "\n".join([f"🔹 {b['name']}" for b in data['buttons']]) or "None"
    curr_name = data['curr_name'] or "Not Set"
    curr_url = "URL Added..✅" if data['curr_url'] else "Not Set"
    
    txt = (
        f"🛠 <b>Custom Button Creator</b>\n\n"
        f"📋 <b>Added so far:</b>\n{btn_list_txt}\n\n"
        f"✨ <b>Current Button:</b>\n"
        f"🏷 Name: <code>{curr_name}</code>\n"
        f"🔗 URL: {curr_url}\n\n"
        "Fill details using buttons below:"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("➕ Add Button Name", callback_data="btn_name"),
               types.InlineKeyboardButton("➕ Add Button URL", callback_data="btn_url"))
    
    if data['curr_name'] and data['curr_url']:
        markup.add(types.InlineKeyboardButton("➕ Add More Buttons", callback_data="btn_add_more"))
    
    markup.add(types.InlineKeyboardButton("💾 Continue & Save", callback_data="btn_save"))
    
    # Strictly edit the dashboard
    try: bot.edit_message_text(txt, uid, data['dash_mid'], reply_markup=markup, parse_mode='HTML')
    except: pass

def set_btn_name(message):
    uid = message.from_user.id
    if uid in TEMP_SLOTS:
        TEMP_SLOTS[uid]['curr_name'] = message.text
        # Cleanup user input and the prompt
        safe_delete(message.chat.id, message.message_id)
        safe_delete(message.chat.id, TEMP_SLOTS[uid]['prompt_mid'])
        refresh_button_menu(None, uid)

def set_btn_url(message):
    uid = message.from_user.id
    if uid in TEMP_SLOTS:
        if not message.text.startswith("http"):
            bot.send_message(uid, "❌ Invalid URL! Must start with http.")
            return
        TEMP_SLOTS[uid]['curr_url'] = message.text
        safe_delete(message.chat.id, message.message_id)
        safe_delete(message.chat.id, TEMP_SLOTS[uid]['prompt_mid'])
        refresh_button_menu(None, uid)

def finalize_slot(message, uid):
    data = TEMP_SLOTS[uid]
    db_data = {
        "title": f"Manual: {data['kw'].title()}",
        "db_mid": int(data['db_mid']),
        "type": "slot",
        "custom_buttons": data['buttons']
    }
    db.add_filter(data['kw'], db_data)
    
    # Edit dashboard to show final success
    bot.edit_message_text(f"✅ <b>Slot '{data['kw']}' Saved Successfully!</b>\nTotal Buttons: {len(data['buttons'])}", uid, data['dash_mid'], parse_mode='HTML')
    del TEMP_SLOTS[uid]
