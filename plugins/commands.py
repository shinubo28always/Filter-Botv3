import time
import threading
from bot_instance import bot
import database as db
import config
from telebot import types

BC_TEMP = {}

def start_broadcasting(targets, data, method, admin_chat_id, status_msg_id):
    success = 0
    failed = 0
    total = len(targets)

    for t_id in targets:
        try:
            if method == "normal":
                bot.copy_message(t_id, data['from_chat'], data['msg_id'])
            else:
                bot.forward_message(t_id, data['from_chat'], data['msg_id'])
            success += 1
        except:
            failed += 1
        
        # Har 20 messages ke baad status update (Bot hang nahi hoga)
        if (success + failed) % 20 == 0:
            try:
                bot.edit_message_text(f"⏳ <b>Broadcasting...</b>\nProgress: {success + failed}/{total}", admin_chat_id, status_msg_id)
            except: pass

    bot.send_message(
        admin_chat_id, 
        f"✅ <b>Broadcast Finished!</b>\n\n🎯 Mode: {data['mode']}\n✔️ Success: {success}\n❌ Failed: {failed}"
    )

@bot.message_handler(commands=['broadcast', 'gbroadcast'])
def broadcast_init(message):
    if not db.is_admin(message.from_user.id): return
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Reply to a message to broadcast.")
    
    mode = "PM" if message.text.startswith("/broadcast") else "Group"
    uid = message.from_user.id
    
    BC_TEMP[uid] = {
        "msg_id": message.reply_to_message.message_id,
        "from_chat": message.chat.id,
        "mode": mode
    }
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🚫 Normal", callback_data="bc_mode|normal"),
        types.InlineKeyboardButton("🏷️ With Tag", callback_data="bc_mode|tag")
    )
    bot.reply_to(message, f"🚀 <b>Broadcast Setup ({mode})</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("bc_mode|"))
def handle_bc_callback(call):
    uid = call.from_user.id
    method = call.data.split("|")[1]
    data = BC_TEMP.get(uid)
    
    if not data: return
    
    targets = db.get_all_users() if data['mode'] == "PM" else db.get_all_groups()
    bot.edit_message_text(f"⏳ Broadcast started for {len(targets)} targets...", call.message.chat.id, call.message.message_id)
    
    # --- THREADING START (Background mein broadcast chalega) ---
    threading.Thread(target=start_broadcasting, args=(targets, data, method, call.message.chat.id, call.message.message_id)).start()
    del BC_TEMP[uid]
