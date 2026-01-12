### This bot is Created By UNRATED CODER --- Join @UNRATED_CODER ###
from bot_instance import bot
from telebot import types
import database as db
import config

TEMP_SLOTS = {}

@bot.message_handler(commands=['add_slot'])
def add_slot_start(message):
    if not db.is_admin(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: return bot.reply_to(message, "⚠️ Usage: /add_slot keyword")
    kw = parts[1].lower().strip()
    TEMP_SLOTS[message.from_user.id] = {"kw": kw, "buttons": [], "show_in_index": False, "index_name": kw.title()}
    msg = bot.reply_to(message, f"📤 <b>Slot Setup:</b> <code>{kw}</code>\n\nSend the message (Text/Media/Buttons) you want to save:", reply_markup=types.ForceReply(selective=True))
    bot.register_next_step_handler(msg, process_slot_content)

def process_slot_content(message):
    uid = message.from_user.id
    try:
        forwarded = bot.forward_message(int(config.DB_CHANNEL_ID), message.chat.id, message.message_id)
        TEMP_SLOTS[uid]['db_mid'] = forwarded.message_id
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("➕ Add Buttons", callback_data="sl_add_btn"),
                   types.InlineKeyboardButton("⏩ Skip", callback_data="sl_skip_btns"))
        bot.send_message(uid, "❓ <b>Step 2: Custom Buttons</b>\nDo you want to add extra buttons?", reply_markup=markup)
    except Exception as e:
        bot.send_message(uid, f"❌ Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith(("sl_", "bt_")))
def handle_slot_steps(call):
    uid = call.from_user.id
    if uid not in TEMP_SLOTS: return bot.answer_callback_query(call.id, "Session Expired!", show_alert=True)

    if call.data == "sl_add_btn":
        refresh_button_menu(call.message, uid)
    elif call.data == "bt_name":
        msg = bot.send_message(uid, "✍️ Enter Button Name:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, set_btn_name)
    elif call.data == "bt_url":
        msg = bot.send_message(uid, "🌐 Enter Button URL:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, set_btn_url)
    elif call.data == "bt_add_more":
        data = TEMP_SLOTS[uid]
        data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        data['curr_name'] = data['curr_url'] = None
        refresh_button_menu(call.message, uid)
    elif call.data in ["sl_skip_btns", "bt_continue"]:
        data = TEMP_SLOTS[uid]
        if data.get('curr_name') and data.get('curr_url'):
            data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        ask_index_step(call.message, uid)
    elif call.data == "sl_ind_yes":
        msg = bot.send_message(uid, "✍️ Enter Name for A-Z Index:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, set_index_name)
    elif call.data == "sl_ind_no":
        finalize_slot(call.message, uid)

def refresh_button_menu(message, uid):
    data = TEMP_SLOTS[uid]
    btn_list = "\n".join([f"🔹 {b['name']}" for b in data['buttons']]) or "None"
    txt = f"🛠 <b>Button Creator</b>\n\n📋 Added:\n{btn_list}\n\n🏷 Name: {data.get('curr_name','Not Set')}\n🔗 URL: {'Added..✅' if data.get('curr_url') else 'Not Set'}"
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("➕ Name", callback_data="bt_name"), types.InlineKeyboardButton("➕ URL", callback_data="bt_url"))
    if data.get('curr_name') and data.get('curr_url'): markup.add(types.InlineKeyboardButton("➕ Add More", callback_data="bt_add_more"))
    markup.add(types.InlineKeyboardButton("💾 Continue", callback_data="bt_continue"))
    bot.edit_message_text(txt, uid, message.message_id, reply_markup=markup)

def set_btn_name(m): 
    TEMP_SLOTS[m.from_user.id]['curr_name'] = m.text
    refresh_button_menu(m, m.from_user.id)
def set_btn_url(m):
    if m.text.startswith("http"): TEMP_SLOTS[m.from_user.id]['curr_url'] = m.text
    refresh_button_menu(m, m.from_user.id)

def ask_index_step(message, uid):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("✅ Yes", callback_data="sl_ind_yes"), types.InlineKeyboardButton("❌ No", callback_data="sl_ind_no"))
    bot.edit_message_text("❓ <b>Step 3: Indexing</b>\nShow in A-Z Index?", uid, message.message_id, reply_markup=markup)

def set_index_name(m):
    uid = m.from_user.id
    TEMP_SLOTS[uid]['show_in_index'] = True
    TEMP_SLOTS[uid]['index_name'] = m.text.strip()
    finalize_slot(m, uid, is_msg=True)

def finalize_slot(message, uid, is_msg=False):
    data = TEMP_SLOTS[uid]
    db.add_filter(data['kw'], {
        "title": data.get('index_name', data['kw'].title()),
        "db_mid": int(data['db_mid']),
        "type": "slot",
        "custom_buttons": data['buttons'],
        "show_in_index": data['show_in_index']
    })
    txt = f"✅ <b>Slot '{data['kw']}' Saved Successfully!</b>"
    if is_msg: bot.send_message(uid, txt)
    else: bot.edit_message_text(txt, uid, message.message_id)
    del TEMP_SLOTS[uid]
