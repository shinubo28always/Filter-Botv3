### This bot is Created By UNRATED CODER --- Join @UNRATED_CODER ###
from bot_instance import bot
from telebot import types
import database as db
import config, html

TEMP_SLOTS = {}

@bot.message_handler(commands=['add_slot'])
def add_slot_start(message):
    if not db.is_admin(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: return bot.reply_to(message, "⚠️ Usage: /add_slot keyword")
    
    kw = parts[1].lower().strip()
    TEMP_SLOTS[message.from_user.id] = {"kw": kw, "buttons": [], "show_in_index": False}
    msg = bot.reply_to(message, f"📤 <b>Slot Setup:</b> <code>{kw}</code>\n\nSend the message (Text/Media/Buttons) you want to save:", reply_markup=types.ForceReply(selective=True))
    bot.register_next_step_handler(msg, process_slot_content)

def process_slot_content(message):
    uid = message.from_user.id
    try:
        forwarded = bot.forward_message(int(config.DB_CHANNEL_ID), message.chat.id, message.message_id)
        TEMP_SLOTS[uid]['db_mid'] = forwarded.message_id
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✅ Show in Index", callback_data="sl_ind_yes"),
                   types.InlineKeyboardButton("❌ Don't Show", callback_data="sl_ind_no"))
        bot.send_message(uid, "❓ <b>Indexing</b>\nDo you want to show this slot in the A-Z Index?", reply_markup=markup)
    except Exception as e:
        bot.send_message(uid, f"❌ Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("sl_ind_"))
def handle_index_choice(call):
    uid = call.from_user.id
    if uid not in TEMP_SLOTS: return
    
    if call.data == "sl_ind_yes":
        msg = bot.send_message(uid, "✍️ <b>Send Name for Index:</b>\n(Example: One Piece Movie 1)", reply_markup=types.ForceReply(selective=True))
        bot.register_next_step_handler(msg, save_index_name)
    else:
        finalize_slot(call.message, uid)

def save_index_name(message):
    uid = message.from_user.id
    TEMP_SLOTS[uid]['show_in_index'] = True
    TEMP_SLOTS[uid]['index_name'] = message.text.strip()
    finalize_slot(message, uid)

def finalize_slot(message, uid):
    data = TEMP_SLOTS[uid]
    db_data = {
        "title": data.get('index_name', f"Slot: {data['kw'].title()}"),
        "db_mid": int(data['db_mid']),
        "type": "slot",
        "show_in_index": data['show_in_index']
    }
    db.add_filter(data['kw'], db_data)
    bot.send_message(uid, f"✅ <b>Manual Slot '{data['kw']}' Added!</b>")
    del TEMP_SLOTS[uid]
