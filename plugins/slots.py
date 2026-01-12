### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

import time
import html
import config
import database as db
from bot_instance import bot
from telebot import types

# Temporary session tracking
TEMP_SLOTS = {}

@bot.message_handler(commands=['add_slot'])
def add_slot_start(message):
    if not db.is_admin(message.from_user.id): return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/add_slot keyword</code>")
    
    kw = parts[1].lower().strip()
    uid = message.from_user.id
    
    # Initialize Session
    TEMP_SLOTS[uid] = {
        "kw": kw,
        "buttons": [],
        "curr_name": None,
        "curr_url": None,
        "db_mid": None,
        "show_in_index": False,
        "index_name": f"Slot: {kw.title()}"
    }
    
    markup = types.ForceReply(selective=True)
    msg = bot.reply_to(message, f"📤 <b>Slot Setup:</b> <code>{kw}</code>\n\nSend the <b>Message (Text/Media/Buttons)</b> you want to save:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_slot_content)

def process_slot_content(message):
    uid = message.from_user.id
    if uid not in TEMP_SLOTS: return
    
    if message.text and message.text.startswith("/"):
        del TEMP_SLOTS[uid]
        return bot.send_message(uid, "❌ Setup cancelled.")

    try:
        # Forward to DB Channel
        db_id = int(config.DB_CHANNEL_ID)
        forwarded = bot.forward_message(db_id, message.chat.id, message.message_id)
        TEMP_SLOTS[uid]['db_mid'] = forwarded.message_id
        
        # Ask for Buttons
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("➕ Add Buttons", callback_data="sl_add_btn"),
                   types.InlineKeyboardButton("⏩ Skip", callback_data="sl_skip_btns"))
        
        bot.send_message(uid, "❓ <b>Step 2: Custom Buttons</b>\nDo you want to add extra buttons to this slot?", reply_markup=markup)
    except Exception as e:
        bot.send_message(uid, f"❌ <b>Error:</b> <code>{str(e)}</code>")
        del TEMP_SLOTS[uid]

# --- CALLBACK HANDLER FOR INTERACTIVE SETUP ---
@bot.callback_query_handler(func=lambda call: call.data.startswith(("sl_", "bt_")))
def handle_slot_steps(call):
    uid = call.from_user.id
    if uid not in TEMP_SLOTS:
        return bot.answer_callback_query(call.id, "❌ Session Expired!", show_alert=True)

    # 1. Start Button Creator
    if call.data == "sl_add_btn" or call.data == "bt_refresh":
        bot.answer_callback_query(call.id)
        refresh_button_menu(call.message, uid)

    # 2. Add Button Name
    elif call.data == "bt_name":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(uid, "✍️ <b>Enter Button Name:</b>", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, set_btn_name)

    # 3. Add Button URL
    elif call.data == "bt_url":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(uid, "🌐 <b>Enter Button URL (https://...):</b>", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, set_btn_url)

    # 4. Save Button and Add More
    elif call.data == "bt_add_more":
        data = TEMP_SLOTS[uid]
        if not data['curr_name'] or not data['curr_url']:
            return bot.answer_callback_query(call.id, "❌ Enter Name and URL first!", show_alert=True)
        
        data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        data['curr_name'] = None
        data['curr_url'] = None
        bot.answer_callback_query(call.id, "Button added to list!")
        refresh_button_menu(call.message, uid)

    # 5. Skip/Finish Buttons -> Go to Index Choice
    elif call.data == "sl_skip_btns" or call.data == "bt_continue":
        bot.answer_callback_query(call.id)
        # If there is a half-filled button, add it
        data = TEMP_SLOTS[uid]
        if data['curr_name'] and data['curr_url']:
            data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        
        ask_index_step(call.message, uid)

    # 6. Index Choice: Yes
    elif call.data == "sl_ind_yes":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(uid, "✍️ <b>Enter Display Name for A-Z Index:</b>\n(e.g. Naruto Season 1)", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, set_index_name)

    # 7. Index Choice: No
    elif call.data == "sl_ind_no":
        bot.answer_callback_query(call.id)
        TEMP_SLOTS[uid]['show_in_index'] = False
        finalize_slot(call.message, uid)

def refresh_button_menu(message, uid):
    data = TEMP_SLOTS[uid]
    btn_list = "\n".join([f"🔹 {b['name']}" for b in data['buttons']]) or "None"
    c_name = data['curr_name'] or "Not Set"
    c_url = "URL Added..✅" if data['curr_url'] else "Not Set"
    
    txt = (
        f"🛠 <b>Button Creator</b>\n\n"
        f"📋 <b>Added Buttons:</b>\n{btn_list}\n\n"
        f"✨ <b>Current Setup:</b>\n"
        f"🏷 Name: <code>{c_name}</code>\n"
        f"🔗 URL: {c_url}\n\n"
        "Fill details using buttons below:"
    )
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("➕ Set Name", callback_data="bt_name"),
               types.InlineKeyboardButton("➕ Set URL", callback_data="bt_url"))
    if data['curr_name'] and data['curr_url']:
        markup.add(types.InlineKeyboardButton("➕ Add More Buttons", callback_data="bt_add_more"))
    markup.add(types.InlineKeyboardButton("💾 Continue to Next Step", callback_data="bt_continue"))
    
    try: bot.edit_message_text(txt, uid, message.message_id, reply_markup=markup, parse_mode='HTML')
    except: bot.send_message(uid, txt, reply_markup=markup, parse_mode='HTML')

def set_btn_name(message):
    uid = message.from_user.id
    if uid in TEMP_SLOTS:
        TEMP_SLOTS[uid]['curr_name'] = message.text
        try: bot.delete_message(uid, message.message_id)
        except: pass
        refresh_button_menu(message, uid)

def set_btn_url(message):
    uid = message.from_user.id
    url = message.text.strip()
    if uid in TEMP_SLOTS:
        if not url.startswith("http"):
            bot.send_message(uid, "❌ <b>Invalid URL!</b> Must start with http or https.")
            return
        TEMP_SLOTS[uid]['curr_url'] = url
        try: bot.delete_message(uid, message.message_id)
        except: pass
        refresh_button_menu(message, uid)

def ask_index_step(message, uid):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("✅ Yes", callback_data="sl_ind_yes"),
               types.InlineKeyboardButton("❌ No", callback_data="sl_ind_no"))
    bot.edit_message_text("❓ <b>Step 3: Indexing</b>\nDo you want to show this slot in the A-Z Index list?", uid, message.message_id, reply_markup=markup)

def set_index_name(message):
    uid = message.from_user.id
    if uid in TEMP_SLOTS:
        TEMP_SLOTS[uid]['show_in_index'] = True
        TEMP_SLOTS[uid]['index_name'] = message.text.strip()
        try: bot.delete_message(uid, message.message_id)
        except: pass
        finalize_slot(message, uid, is_from_step=True)

def finalize_slot(message, uid, is_from_step=False):
    data = TEMP_SLOTS[uid]
    
    # DB Format
    db_data = {
        "title": data['index_name'],
        "db_mid": int(data['db_mid']),
        "type": "slot",
        "custom_buttons": data['buttons'],
        "show_in_index": data['show_in_index']
    }
    
    db.add_filter(data['kw'], db_data)
    
    success_txt = f"✅ <b>Manual Slot Added!</b>\n\nKeyword: <code>{data['kw']}</code>\nIndex Name: <code>{data['index_name']}</code>\nButtons: {len(data['buttons'])}"
    
    if is_from_step:
        bot.send_message(uid, success_txt, parse_mode='HTML')
    else:
        bot.edit_message_text(success_txt, uid, message.message_id, parse_mode='HTML')
    
    del TEMP_SLOTS[uid]

### Support Us @UNRATED_CODER ###
