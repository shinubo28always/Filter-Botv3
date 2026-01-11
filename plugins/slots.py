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

# Temporary state tracking for multi-step setup
TEMP_SLOTS = {}

def safe_delete(chat_id, msg_id):
    """Message delete karne ka safe tareeka"""
    try: 
        bot.delete_message(chat_id, msg_id)
    except: 
        pass

# ---------------- STEP 1: INITIALIZE SETUP ----------------
@bot.message_handler(commands=['add_slot'])
def add_slot_start(message):
    if not db.is_admin(message.from_user.id): 
        return
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/add_slot keyword</code>")
    
    kw = parts[1].lower().strip()
    uid = message.from_user.id
    
    # State data initialization
    TEMP_SLOTS[uid] = {
        "kw": kw,
        "buttons": [],
        "curr_name": None,
        "curr_url": None,
        "dash_mid": None,   # Main Menu Message ID
        "prompt_mid": None  # Current Input Prompt ID
    }
    
    markup = types.ForceReply(selective=True)
    msg = bot.reply_to(
        message, 
        f"📤 <b>Step 1: Content Setup</b>\nKeyword: <code>{kw}</code>\n\n<b>Now send the Message (Text/Media) you want to save:</b>", 
        reply_markup=markup
    )
    TEMP_SLOTS[uid]['prompt_mid'] = msg.message_id
    bot.register_next_step_handler(msg, process_slot_content)

# ---------------- STEP 2: PROCESS CONTENT ----------------
def process_slot_content(message):
    uid = message.from_user.id
    if uid not in TEMP_SLOTS: 
        return
    
    # Cleanup user input and the first prompt
    safe_delete(message.chat.id, TEMP_SLOTS[uid]['prompt_mid'])
    safe_delete(message.chat.id, message.message_id)

    try:
        # User ka message DB Channel mein copy karein (Real-time content + buttons)
        db_msg = bot.copy_message(config.DB_CHANNEL_ID, message.chat.id, message.message_id)
        TEMP_SLOTS[uid]['db_mid'] = db_msg.message_id
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("➕ Add Custom Buttons", callback_data="slot_add_btn"),
            types.InlineKeyboardButton("⏩ No, Skip This", callback_data="slot_skip")
        )
        
        # Dashboard message send karein
        dash = bot.send_message(
            uid, 
            "❓ <b>Step 2: Buttons Setup</b>\nDo you want to add custom buttons to this filter?", 
            reply_markup=markup,
            parse_mode='HTML'
        )
        TEMP_SLOTS[uid]['dash_mid'] = dash.message_id
        
    except Exception as e:
        bot.send_message(uid, f"❌ <b>Error:</b> <code>{str(e)}</code>")

# ---------------- STEP 3: CALLBACK HANDLER (INTERACTIVE MENU) ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith(("slot_", "btn_")))
def handle_slot_callbacks(call):
    uid = call.from_user.id
    if uid not in TEMP_SLOTS:
        return bot.answer_callback_query(call.id, "❌ Session Expired! Please start again.", show_alert=True)

    # A. SKIP BUTTONS
    if call.data == "slot_skip":
        bot.answer_callback_query(call.id, "Saving without extra buttons...")
        finalize_slot(call.message, uid)

    # B. REFRESH/START BUTTON ADDING
    elif call.data == "slot_add_btn" or call.data == "btn_refresh":
        bot.answer_callback_query(call.id)
        refresh_button_menu(call.message, uid)

    # C. INPUT BUTTON NAME
    elif call.data == "btn_name":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(uid, "✍️ <b>Send Button Name:</b>", reply_markup=types.ForceReply())
        TEMP_SLOTS[uid]['prompt_mid'] = msg.message_id
        bot.register_next_step_handler(msg, set_btn_name)

    # D. INPUT BUTTON URL
    elif call.data == "btn_url":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(uid, "🌐 <b>Send Button URL (starting with http/https):</b>", reply_markup=types.ForceReply())
        TEMP_SLOTS[uid]['prompt_mid'] = msg.message_id
        bot.register_next_step_handler(msg, set_btn_url)

    # E. ADD MORE BUTTONS (SAVE CURRENT TO LIST)
    elif call.data == "btn_add_more":
        data = TEMP_SLOTS[uid]
        if not data['curr_name'] or not data['curr_url']:
            return bot.answer_callback_query(call.id, "❌ Please fill both Name and URL first!", show_alert=True)
        
        data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        data['curr_name'] = None
        data['curr_url'] = None
        bot.answer_callback_query(call.id, "Button added to list! ✅")
        refresh_button_menu(call.message, uid)

    # F. SAVE AND FINALIZE
    elif call.data == "btn_save":
        bot.answer_callback_query(call.id, "Saving Filter...")
        data = TEMP_SLOTS[uid]
        # Check if there's an unsaved button in fields
        if data['curr_name'] and data['curr_url']:
            data['buttons'].append({"name": data['curr_name'], "url": data['curr_url']})
        finalize_slot(call.message, uid)

# ---------------- HELPER: REFRESH DASHBOARD ----------------
def refresh_button_menu(message, uid):
    data = TEMP_SLOTS[uid]
    
    # Buttons already added to the list
    btn_list_txt = "\n".join([f"🔹 {b['name']}" for b in data['buttons']]) or "<i>None</i>"
    
    # Current working fields
    curr_name = html.escape(data['curr_name']) if data['curr_name'] else "Not Set"
    curr_url = "URL Added.. ✅" if data['curr_url'] else "Not Set"
    
    txt = (
        f"🛠 <b>Custom Button Creator</b>\n\n"
        f"📋 <b>Added Buttons so far:</b>\n{btn_list_txt}\n\n"
        f"✨ <b>Current Active Field:</b>\n"
        f"🏷 Name: <code>{curr_name}</code>\n"
        f"🔗 URL: {curr_url}\n\n"
        "Fill details using the options below:"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("➕ Add Button Name", callback_data="btn_name"),
        types.InlineKeyboardButton("➕ Add Button URL", callback_data="btn_url")
    )
    
    # Show "Add More" only if current fields are full
    if data['curr_name'] and data['curr_url']:
        markup.add(types.InlineKeyboardButton("➕ Save & Add More Buttons", callback_data="btn_add_more"))
    
    markup.add(types.InlineKeyboardButton("💾 Finalize & Save Filter", callback_data="btn_save"))
    
    try:
        bot.edit_message_text(txt, uid, data['dash_mid'], reply_markup=markup, parse_mode='HTML')
    except:
        pass

# ---------------- STEP 4: PROCESS BUTTON INPUTS ----------------
def set_btn_name(message):
    uid = message.from_user.id
    if uid in TEMP_SLOTS:
        TEMP_SLOTS[uid]['curr_name'] = message.text
        # Cleanup user reply and bot prompt
        safe_delete(message.chat.id, message.message_id)
        safe_delete(message.chat.id, TEMP_SLOTS[uid]['prompt_mid'])
        refresh_button_menu(None, uid)

def set_btn_url(message):
    uid = message.from_user.id
    if uid in TEMP_SLOTS:
        if not message.text.startswith("http"):
            bot.send_message(uid, "❌ <b>Invalid URL!</b> Must start with <code>http</code> or <code>https</code>.")
            return
        TEMP_SLOTS[uid]['curr_url'] = message.text
        # Cleanup
        safe_delete(message.chat.id, message.message_id)
        safe_delete(message.chat.id, TEMP_SLOTS[uid]['prompt_mid'])
        refresh_button_menu(None, uid)

# ---------------- STEP 5: SAVE TO DATABASE ----------------
def finalize_slot(message, uid):
    data = TEMP_SLOTS[uid]
    
    db_data = {
        "title": f"Manual: {data['kw'].title()}",
        "db_mid": int(data['db_mid']),
        "type": "slot",
        "custom_buttons": data['buttons'] # List of {"name": "...", "url": "..."}
    }
    
    # MongoDB save call
    db.add_filter(data['kw'], db_data)
    
    final_txt = (
        f"✅ <b>Filter Saved Successfully!</b>\n\n"
        f"🏷 Keyword: <code>{data['kw']}</code>\n"
        f"🔘 Buttons Added: <code>{len(data['buttons'])}</code>\n\n"
        f"<i>Bot will now deliver this message when users search the keyword.</i>"
    )
    
    try:
        bot.edit_message_text(final_txt, uid, data['dash_mid'], parse_mode='HTML')
    except:
        bot.send_message(uid, final_txt, parse_mode='HTML')
        
    # Remove user from memory
    del TEMP_SLOTS[uid]

### Created By UNRATED CODER ™ TEAM --- TG - @UNRATED_CODER ###
