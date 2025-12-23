import time
import threading
from bot_instance import bot
import database as db
import config
from telebot import types

# Temporary storage for broadcast setup
BC_SETUP = {}

def run_broadcast(targets, data, method, admin_id, status_mid):
    success = 0
    failed = 0
    total = len(targets)
    
    for t_id in targets:
        try:
            if method == "normal":
                # Copy message (No forward tag)
                bot.copy_message(t_id, data['from_chat'], data['msg_id'])
            else:
                # Forward (With original tag)
                bot.forward_message(t_id, data['from_chat'], data['msg_id'])
            success += 1
        except:
            failed += 1
        
        # Har 25 messages ke baad progress update
        if (success + failed) % 25 == 0:
            try:
                bot.edit_message_text(f"🚀 <b>Broadcasting...</b>\n\nProgress: {success + failed}/{total}\nSuccess: {success}\nFailed: {failed}", admin_id, status_mid)
            except: pass
            time.sleep(1) # API limit se bachne ke liye

    bot.send_message(admin_id, f"✅ <b>Broadcast Completed!</b>\n\nTotal: {total}\nSuccess: {success}\nFailed: {failed}")

@bot.message_handler(commands=['broadcast', 'gbroadcast'])
def init_bc(message):
    if not db.is_admin(message.from_user.id): return
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Reply to a message to broadcast.")
    
    uid = message.from_user.id
    mode = "PM" if "/broadcast" in message.text else "Group"
    
    BC_SETUP[uid] = {
        "msg_id": message.reply_to_message.message_id,
        "from_chat": message.chat.id,
        "mode": mode
    }
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🚫 Normal (No Tag)", callback_data="bc_act|normal"),
        types.InlineKeyboardButton("🏷️ With Tag", callback_data="bc_act|tag")
    )
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="bc_act|cancel"))
    
    bot.reply_to(message, f"<b>Setup Broadcast for {mode}</b>\nSelect method:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("bc_act|"))
def handle_bc_choice(call):
    uid = call.from_user.id
    choice = call.data.split("|")[1]
    
    if choice == "cancel":
        if uid in BC_SETUP: del BC_SETUP[uid]
        return bot.edit_message_text("❌ Broadcast cancelled.", call.message.chat.id, call.message.message_id)

    data = BC_SETUP.get(uid)
    if not data:
        return bot.answer_callback_query(call.id, "Setup Expired!", show_alert=True)

    targets = db.get_all_users() if data['mode'] == "PM" else db.get_all_groups()
    if not targets:
        return bot.edit_message_text("❌ No targets found in database!", call.message.chat.id, call.message.message_id)

    bot.edit_message_text(f"⏳ Starting {choice} broadcast to {len(targets)} {data['mode']}s...", call.message.chat.id, call.message.message_id)
    
    # Background Threading
    threading.Thread(target=run_broadcast, args=(targets, data, choice, call.message.chat.id, call.message.message_id)).start()
    del BC_SETUP[uid]
