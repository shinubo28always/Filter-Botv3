import time
import threading
from bot_instance import bot
import database as db
from telebot import types, apihelper

def run_broadcast(targets, msg_id, from_chat, mode, admin_id, status_mid):
    done = 0
    blocked = 0
    deleted = 0
    not_found = 0
    total = len(targets)
    
    for t_id in targets:
        try:
            bot.copy_message(t_id, from_chat, msg_id)
            done += 1
        except apihelper.ApiTelegramException as e:
            if e.description == "Forbidden: bot was blocked by the user":
                blocked += 1
            elif "chat not found" in e.description.lower():
                if mode == "Group": not_found += 1
                else: deleted += 1
            else:
                deleted += 1
        except:
            deleted += 1
        
        # Har 15 msgs par update
        if (done + blocked + deleted + not_found) % 15 == 0:
            try:
                bot.edit_message_text(f"🚀 <b>Broadcasting...</b>\nProgress: {done+blocked+deleted+not_found}/{total}", admin_id, status_mid)
            except: pass

    # Final Summary as requested
    if mode == "PM":
        summary = (
            f"✅ <b>PM Broadcast Done!</b>\n\n"
            f"👤 Total members: {total}\n"
            f"✔️ Done: {done}\n"
            f"🚫 Blocked: {blocked}\n"
            f"🗑️ Deleted: {deleted}"
        )
    else:
        summary = (
            f"✅ <b>Group Broadcast Done!</b>\n\n"
            f"🏘️ Total Chat: {total}\n"
            f"✔️ Done: {done}\n"
            f"❌ Not Find: {not_found}"
        )
    
    bot.send_message(admin_id, summary)

@bot.message_handler(commands=['broadcast', 'gbroadcast'])
def bc_init(message):
    if not db.is_admin(message.from_user.id): return
    if not message.reply_to_message:
        return bot.reply_to(message, "⚠️ Reply to a message to broadcast.")
    
    mode = "PM" if "broadcast" in message.text and "gbroadcast" not in message.text else "Group"
    targets = db.get_all_users() if mode == "PM" else db.get_all_groups()
    
    if not targets:
        return bot.reply_to(message, "❌ Database is empty!")

    status = bot.reply_to(message, f"⏳ Starting {mode} broadcast to {len(targets)} targets...")
    
    threading.Thread(
        target=run_broadcast, 
        args=(targets, message.reply_to_message.message_id, message.chat.id, mode, message.chat.id, status.message_id)
    ).start()
