### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

from bot_instance import bot
from telebot import types
import database as db
import config
import html

# In-memory session tracking
TEMP_SLOTS = {}

@bot.message_handler(commands=['add_slot'])
def add_slot_start(message):
    if not db.is_admin(message.from_user.id): return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/add_slot keyword</code>")
    
    kw = parts[1].lower().strip()
    uid = message.from_user.id
    
    # Initialize Session Data
    TEMP_SLOTS[uid] = {
        "kw": kw,
        "buttons": [],
        "curr_name": None,
        "curr_url": None,
        "db_mid": None,
        "show_in_index": False,
        "index_name": kw.title(),
        "menu_msg_id": None # To keep editing the same menu
    }
    
    markup = types.ForceReply(selective=True)
    msg = bot.reply_to(message, f"📤 <b>Slot:</b> <code>{kw}</code>\n\nSend the <b>Message (Text/Media/Buttons)</b> you want to save:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_slot_content)

def process_slot_content(message):
    uid = message.from_user.id
    if uid not in TEMP_SLOTS: return

    try:
        # 1. Forward content to DB Channel
        db_id = int(config.DB_CHANNEL_ID)
        forwarded = bot.forward_message(db_id, message.chat.id, message.message_id)
        TEMP_SLOTS[uid]['db_mid'] = forwarded.message_id
        
        # 2. Show Button Setup Menu
        show_button_menu(uid, message.chat.id)
    except Exception as e:
        bot.send_message(uid, f"❌ <b>Error:</b> {str(e)}")

def show_button_menu(uid, chat_id, edit=False):
    data = TEMP_SLOTS[uid]
    btn_list = "\n".join([f"🔹 {b['name']}" for b in data['buttons']]) or "None"
    
    c_name = data['curr_name'] if data['curr_name'] else "Not Set"
    c_url = "URL Added..✅" if data['curr_url'] else "Not Set"
    
    txt = (
        f"🛠 <b>Custom Button Creator</b>\n\n"
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
        markup.add(types.InlineKeyboardButton("✅ Add More Buttons", callback_data="bt_add_list"))
    
    markup.add(types.InlineKeyboardButton("💾 Next Step (Indexing)", callback_data="bt_next_step"))

    if edit and data['menu_msg_id']:
        try: bot.edit_message_text(txt, chat_id, data['menu_msg_id'], reply_markup=markup, parse_mode='HTML')
        except: pass
    else:
        sent = bot.send_message(chat_id, txt, reply_markup=markup, parse_mode='HTML')
        TEMP_SLOTS[uid]['menu_msg_id'] = sent.message_id

# --- CALLBACK HANDLERS ---
@bot.callback_query_handler(func=lambda call: call.data.startswith(("sl_", "bt_", "pick_")))
def handle_slot_callbacks(call):
    uid = call.from_user.id
    if uid not in TEMP_SLOTS:
        return bot.answer_callback_query(call.id, "❌ Session Expired! Start again.", show_alert=True)

    bot.answer_callback_query(call.id)

    if call.data == "bt_name":
        msg = bot.send_message(uid, "✍️ <b>Enter Button Name:</b>", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, save_btn_name)

    elif call.data == "bt_url":
        msg = bot.send_message(uid, "🌐 <b>Enter Button URL:</b>", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, save_btn_url)

    elif call.data == "bt_add_list":
        data = TEMP_SLOTS[uid]
        data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        data['curr_name'] = data['curr_url'] = None
        show_button_menu(uid, call.message.chat.id, edit=True)

    elif call.data == "bt_next_step":
        data = TEMP_SLOTS[uid]
        # Auto-save current if not empty
        if data['curr_name'] and data['curr_url']:
            data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        
        # Ask for Indexing
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✅ Yes, Show in Index", callback_data="sl_ind_yes"),
                   types.InlineKeyboardButton("❌ No, Hide it", callback_data="sl_ind_no"))
        bot.edit_message_text("❓ <b>Step 3: Indexing</b>\nDo you want to show this slot in the A-Z Index?", uid, data['menu_msg_id'], reply_markup=markup)

    elif call.data == "sl_ind_yes":
        msg = bot.send_message(uid, "✍️ <b>Enter Display Name for Index:</b>", reply_markup=types.ForceReply())
        bot.register_next_step_handler(msg, save_index_name)

    elif call.data == "sl_ind_no":
        TEMP_SLOTS[uid]['show_in_index'] = False
        finalize_slot_save(uid, call.message.chat.id)

# --- NEXT STEP HANDLERS ---
def save_btn_name(message):
    uid = message.from_user.id
    if uid in TEMP_SLOTS:
        TEMP_SLOTS[uid]['curr_name'] = message.text
        try: bot.delete_message(uid, message.message_id) # Cleanup user msg
        except: pass
        show_button_menu(uid, uid, edit=True)

def save_btn_url(message):
    uid = message.from_user.id
    url = message.text.strip()
    if uid in TEMP_SLOTS:
        if not url.startswith("http"):
            bot.send_message(uid, "❌ <b>Invalid URL!</b> Link must start with http/https. Try again:")
            return bot.register_next_step_handler(message, save_btn_url)
        
        TEMP_SLOTS[uid]['curr_url'] = url
        try: bot.delete_message(uid, message.message_id) # Cleanup user msg
        except: pass
        show_button_menu(uid, uid, edit=True)

def save_index_name(message):
    uid = message.from_user.id
    if uid in TEMP_SLOTS:
        TEMP_SLOTS[uid]['show_in_index'] = True
        TEMP_SLOTS[uid]['index_name'] = message.text.strip()
        try: bot.delete_message(uid, message.message_id)
        except: pass
        finalize_slot_save(uid, uid, is_new_msg=True)

def finalize_slot_save(uid, chat_id, is_new_msg=False):
    data = TEMP_SLOTS[uid]
    
    db_data = {
        "title": data.get('index_name', data['kw'].title()),
        "db_mid": int(data['db_mid']),
        "type": "slot",
        "custom_buttons": data['buttons'],
        "show_in_index": data['show_in_index']
    }
    
    db.add_filter(data['kw'], db_data)
    
    res_text = f"✅ <b>Slot '{data['kw']}' Saved Successfully!</b>"
    
    if is_new_msg:
        bot.send_message(uid, res_text, parse_mode='HTML')
    else:
        bot.edit_message_text(res_text, uid, data['menu_msg_id'], parse_mode='HTML')
    
    del TEMP_SLOTS[uid]

### Bot by UNRATED CODER --- Support @UNRATED_CODER ###
