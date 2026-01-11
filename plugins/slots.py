### This bot is Created By UNRATED CODER --- Join @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

import time
import config
import database as db
from bot_instance import bot
from telebot import types

# Temporary storage for slot setup
TEMP_SLOTS = {}

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
        "db_mid": None
    }
    
    markup = types.ForceReply(selective=True)
    msg = bot.reply_to(message, f"📤 <b>Slot Setup:</b> <code>{kw}</code>\n\nSend the <b>Message (Text/Media)</b> you want to save:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_slot_content)

def process_slot_content(message):
    uid = message.from_user.id
    if uid not in TEMP_SLOTS: return

    try:
        # Forward to DB channel to preserve original content
        forwarded = bot.forward_message(int(config.DB_CHANNEL_ID), message.chat.id, message.message_id)
        TEMP_SLOTS[uid]['db_mid'] = forwarded.message_id
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("➕ Add Custom Buttons", callback_data="sl_add_btn"),
            types.InlineKeyboardButton("⏩ No, Skip This", callback_data="sl_skip")
        )
        bot.send_message(uid, "❓ <b>Step 2: Buttons</b>\nDo you want to add extra custom buttons to this slot?", reply_markup=markup)
    except Exception as e:
        bot.send_message(uid, f"❌ <b>Error:</b> <code>{str(e)}</code>")
        del TEMP_SLOTS[uid]

@bot.callback_query_handler(func=lambda call: call.data.startswith(("sl_", "bt_")))
def handle_slot_callbacks(call):
    uid = call.from_user.id
    if uid not in TEMP_SLOTS:
        return bot.answer_callback_query(call.id, "Session Expired! Restart /add_slot", show_alert=True)

    if call.data == "sl_skip":
        finalize_slot(call.message, uid)
    elif call.data == "sl_add_btn" or call.data == "bt_refresh":
        refresh_button_menu(call.message, uid)
    elif call.data == "bt_name":
        msg = bot.send_message(uid, "✍️ <b>Send Button Name:</b>", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, set_btn_name)
    elif call.data == "bt_url":
        msg = bot.send_message(uid, "🌐 <b>Send Button URL:</b>", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, set_btn_url)
    elif call.data == "bt_add_more":
        data = TEMP_SLOTS[uid]
        if not data['curr_name'] or not data['curr_url']:
            return bot.answer_callback_query(call.id, "Set Name and URL first!", show_alert=True)
        data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        data['curr_name'] = data['curr_url'] = None
        refresh_button_menu(call.message, uid)
    elif call.data == "bt_save":
        data = TEMP_SLOTS[uid]
        if data['curr_name'] and data['curr_url']:
            data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        finalize_slot(call.message, uid)

def refresh_button_menu(message, uid):
    data = TEMP_SLOTS[uid]
    btn_list = "\n".join([f"🔹 {b['name']}" for b in data['buttons']]) or "None"
    txt = (
        f"🛠 <b>Button Creator</b>\n\n"
        f"📋 <b>Added:</b>\n{btn_list}\n\n"
        f"✨ <b>Current:</b>\n"
        f"🏷 Name: <code>{data['curr_name'] or 'Not Set'}</code>\n"
        f"🔗 URL: {'Added ✅' if data['curr_url'] else 'Not Set'}"
    )
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("➕ Name", callback_data="bt_name"),
               types.InlineKeyboardButton("➕ URL", callback_data="bt_url"))
    if data['curr_name'] and data['curr_url']:
        markup.add(types.InlineKeyboardButton("➕ Add More", callback_data="bt_add_more"))
    markup.add(types.InlineKeyboardButton("💾 Finish & Save", callback_data="bt_save"))
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
    if uid in TEMP_SLOTS:
        if not message.text.startswith("http"):
            bot.send_message(uid, "❌ Invalid URL! Start with http.")
            return
        TEMP_SLOTS[uid]['curr_url'] = message.text
        try: bot.delete_message(uid, message.message_id)
        except: pass
        refresh_button_menu(message, uid)

def finalize_slot(message, uid):
    data = TEMP_SLOTS[uid]
    db_data = {
        "title": f"Slot: {data['kw'].title()}",
        "db_mid": int(data['db_mid']),
        "type": "slot",
        "custom_buttons": data['buttons']
    }
    db.add_filter(data['kw'], db_data)
    bot.edit_message_text(f"✅ <b>Manual Slot '{data['kw']}' Saved!</b>", uid, message.message_id)
    del TEMP_SLOTS[uid]
