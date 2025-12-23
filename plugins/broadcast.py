import time, threading
from bot_instance import bot
from telebot import apihelper, types
import database as db

def run_bc(targets, mid, f_chat, mode, admin_id, s_mid):
    done = blocked = deleted = unsuc = 0
    total = len(targets)
    
    for t_id in targets:
        try:
            bot.copy_message(t_id, f_chat, mid)
            done += 1
        except apihelper.ApiTelegramException as e:
            if e.error_code == 403: blocked += 1; db.del_user(t_id)
            elif e.error_code == 400: deleted += 1; db.del_user(t_id)
            else: unsuc += 1
        except: unsuc += 1
        
        if (done + blocked + deleted + unsuc) % 20 == 0:
            try: bot.edit_message_text(f"⏳ Broadcast: {done+blocked+deleted+unsuc}/{total}", admin_id, s_mid)
            except: pass

    res = f"<b><u>Broadcast Completed ({mode})</u></b>\n\nTotal: {total}\nSuccessful: {done}\nBlocked: {blocked}\nDeleted: {deleted}"
    bot.send_message(admin_id, res)

@bot.message_handler(commands=['broadcast', 'gbroadcast'])
def bc_handler(message):
    if not db.is_admin(message.from_user.id): return
    if not message.reply_to_message: return bot.reply_to(message, "Reply to a message.")
    
    mode = "PM" if "gbroadcast" not in message.text else "Group"
    targets = db.get_all_users() if mode == "PM" else db.get_all_groups()
    
    s = bot.reply_to(message, "<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ....</i>")
    threading.Thread(target=run_bc, args=(targets, message.reply_to_message.message_id, message.chat.id, mode, message.chat.id, s.message_id)).start()
