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
    if len(parts) < 2: return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/add_slot keyword</code>")
    kw = parts[1].lower().strip()
    uid = message.from_user.id
    TEMP_SLOTS[uid] = {"kw": kw, "buttons": [], "show_in_index": False, "index_name": kw.title()}
    markup = types.ForceReply(selective=True)
    msg = bot.reply_to(message, f"📤 <b>Slot:</b> <code>{kw}</code>\n\nSend the message (Text/Media/Buttons) you want to save:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_slot_content)

def process_slot_content(message):
    uid = message.from_user.id
    try:
        forwarded = bot.forward_message(int(config.DB_CHANNEL_ID), message.chat.id, message.message_id)
        TEMP_SLOTS[uid]['db_mid'] = forwarded.message_id
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("➕ Add Buttons", callback_data="sl_btn"),
                   types.InlineKeyboardButton("⏩ Skip", callback_data="sl_skip_btn"))
        bot.send_message(uid, "❓ <b>Step 2: Buttons</b>\nDo you want custom buttons?", reply_markup=markup)
    except Exception as e: bot.send_message(uid, f"❌ Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith(("sl_", "bt_")))
def handle_slot_flow(call):
    uid = call.from_user.id
    if uid not in TEMP_SLOTS: return bot.answer_callback_query(call.id, "Session Expired!", show_alert=True)

    if call.data == "sl_btn":
        refresh_btn_menu(call.message, uid)
    elif call.data == "bt_name":
        msg = bot.send_message(uid, "✍️ Enter Button Name:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, lambda m: set_name(m, uid))
    elif call.data == "bt_url":
        msg = bot.send_message(uid, "🌐 Enter URL:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, lambda m: set_url(m, uid))
    elif call.data == "bt_add":
        data = TEMP_SLOTS[uid]
        data['buttons'].append({"name": data['curr_n'], "url": data['curr_u']})
        data['curr_n'] = data['curr_u'] = None
        refresh_btn_menu(call.message, uid)
    elif call.data in ["sl_skip_btn", "bt_done"]:
        if call.data == "bt_done" and TEMP_SLOTS[uid].get('curr_n'):
            TEMP_SLOTS[uid]['buttons'].append({"name": TEMP_SLOTS[uid]['curr_n'], "url": TEMP_SLOTS[uid]['curr_u']})
        ask_index(call.message, uid)
    elif call.data == "sl_ind_y":
        msg = bot.send_message(uid, "✍️ Enter Name for Index:", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, lambda m: set_idx_name(m, uid))
    elif call.data == "sl_ind_n":
        finalize(call.message, uid)

def refresh_btn_menu(message, uid):
    data = TEMP_SLOTS[uid]
    btns = "\n".join([f"🔹 {b['name']}" for b in data['buttons']]) or "None"
    txt = f"🛠 <b>Buttons</b>\n\nAdded:\n{btns}\n\nCurrent: {data.get('curr_n','None')} | {data.get('curr_u','None')}"
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("➕ Name", callback_data="bt_name"), types.InlineKeyboardButton("➕ URL", callback_data="bt_url"))
    if data.get('curr_n') and data.get('curr_u'): markup.add(types.InlineKeyboardButton("➕ Add More", callback_data="bt_add"))
    markup.add(types.InlineKeyboardButton("💾 Next Step", callback_data="bt_done"))
    bot.edit_message_text(txt, uid, message.message_id, reply_markup=markup)

def set_name(m, uid): TEMP_SLOTS[uid]['curr_n'] = m.text; refresh_btn_menu(m, uid)
def set_url(m, uid): 
    if m.text.startswith("http"): TEMP_SLOTS[uid]['curr_u'] = m.text
    refresh_btn_menu(m, uid)

def ask_index(message, uid):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("✅ Yes", callback_data="sl_ind_y"), types.InlineKeyboardButton("❌ No", callback_data="sl_ind_n"))
    bot.edit_message_text("❓ <b>Indexing</b>\nShow in A-Z Index?", uid, message.message_id, reply_markup=markup)

def set_idx_name(m, uid):
    TEMP_SLOTS[uid]['show_in_index'] = True
    TEMP_SLOTS[uid]['index_name'] = m.text.strip()
    finalize(m, uid, is_m=True)

def finalize(message, uid, is_m=False):
    data = TEMP_SLOTS[uid]
    db.add_filter(data['kw'], {"title": data['index_name'], "db_mid": int(data['db_mid']), "type": "slot", "custom_buttons": data['buttons'], "show_in_index": data['show_in_index']})
    txt = f"✅ <b>Slot '{data['kw']}' Saved!</b>"
    if is_m: bot.send_message(uid, txt)
    else: bot.edit_message_text(txt, uid, message.message_id)
    del TEMP_SLOTS[uid]
