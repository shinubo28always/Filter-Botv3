import time
from bot_instance import bot
import database as db
import config
from telebot import types

# Temporary storage for broadcast data
BC_TEMP = {}

@bot.message_handler(commands=['broadcast', 'gbroadcast'])
def broadcast_init(message):
    if not db.is_admin(message.from_user.id): return
    
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ <b>Error:</b> Kisi message ka <b>Reply</b> karke command dein.")
    
    mode = "PM" if message.text.startswith("/broadcast") else "Group"
    uid = message.from_user.id
    
    # Save broadcast info
    BC_TEMP[uid] = {
        "msg_id": message.reply_to_message.message_id,
        "from_chat": message.chat.id,
        "mode": mode
    }
    
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🚫 Normal (No Tag)", callback_data="bc_mode|normal"),
        types.InlineKeyboardButton("🏷️ With Tag", callback_data="bc_mode|tag")
    )
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="bc_cancel"))
    
    bot.reply_to(
        message, 
        f"🚀 <b>Broadcast Setup ({mode})</b>\n\nKaise forward karna chahte hain?", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("bc_"))
def handle_bc_callback(call):
    uid = call.from_user.id
    if uid not in BC_TEMP:
        return bot.answer_callback_query(call.id, "Setup Expired!", show_alert=True)

    if call.data == "bc_cancel":
        del BC_TEMP[uid]
        bot.edit_message_text("❌ Broadcast Cancelled.", call.message.chat.id, call.message.message_id)
        return

    method = call.data.split("|")[1] # 'normal' or 'tag'
    data = BC_TEMP[uid]
    
    # Target list nikalna
    targets = db.get_all_users() if data['mode'] == "PM" else db.get_all_groups()
    total = len(targets)
    
    bot.edit_message_text(f"⏳ <b>Broadcasting to {total} {data['mode']}s...</b>", call.message.chat.id, call.message.message_id)
    
    success = 0
    failed = 0
    
    for t_id in targets:
        try:
            if method == "normal":
                # Copy message (No forward tag)
                bot.copy_message(t_id, data['from_chat'], data['msg_id'])
            else:
                # Forward message (Preserves original source tag)
                bot.forward_message(t_id, data['from_chat'], data['msg_id'])
            success += 1
        except:
            failed += 1
            # Optional: Remove inactive groups/users
            # if data['mode'] == "Group": db.remove_group(t_id)
            
        # Update progress every 20 msgs
        if (success + failed) % 20 == 0:
            try: bot.edit_message_text(f"⏳ <b>Progress:</b> {success + failed}/{total}", call.message.chat.id, call.message.message_id)
            except: pass
            
    bot.send_message(
        call.message.chat.id, 
        f"✅ <b>Broadcast Finished!</b>\n\n"
        f"🎯 Mode: {data['mode']} ({method.upper()})\n"
        f"✔️ Success: {success}\n"
        f"❌ Failed: {failed}"
    )
    del BC_TEMP[uid]
