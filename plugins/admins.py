from bot_instance import bot
import config
import database as db
from telebot import types
import html

@bot.message_handler(commands=['add_admin'])
def add_admin_handler(message):
    # Only Owner can add
    if str(message.from_user.id) != str(config.OWNER_ID):
        return bot.reply_to(message, "❌ <b>Only the Main Owner can use this!</b>")
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/add_admin USER_ID</code>")
        
        target_id = parts[1].strip()

        # 1. Check if ID is numeric
        if not target_id.isdigit():
            return bot.reply_to(message, "❌ <b>Invalid ID!</b> Please provide a numeric User ID (e.g. 7009167334).")

        # 2. Check if user is in Database
        if not db.present_user(target_id):
            return bot.reply_to(message, "❌ <b>User Not Found!</b>\nBande ne abhi tak bot start nahi kiya hai ya wo database mein nahi hai.")

        # 3. Try to notify the new Admin
        owner_name = html.escape(message.from_user.first_name)
        owner_id = message.from_user.id
        owner_mention = f"<a href='tg://user?id={owner_id}'>{owner_name}</a>"

        try:
            notification_text = (
                "🎉 <b>Congratulations!</b>\n\n"
                f"Aapko {owner_mention} ne is bot ka <b>Admin</b> bana diya hai.\n"
                "Ab aap filters aur channels manage kar sakte hain."
            )
            bot.send_message(target_id, notification_text)
        except Exception as e:
            return bot.reply_to(message, f"❌ <b>Error:</b> Bot user ko message nahi bhej pa raha.\nShayad usne bot block kar diya hai.")

        # 4. Final Save to DB
        db.add_admin(target_id)
        bot.reply_to(message, f"✅ <b>Success!</b>\nUser <code>{target_id}</code> is now an Admin and has been notified.")

    except Exception as e:
        bot.reply_to(message, f"❌ <b>Critical Error:</b> {e}")

@bot.message_handler(commands=['del_admin'])
def del_admin_handler(message):
    if str(message.from_user.id) != str(config.OWNER_ID):
        return bot.reply_to(message, "❌ <b>Only the Main Owner can remove admins!</b>")
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/del_admin USER_ID</code>")
        
        target_id = parts[1].strip()
        
        if target_id == str(config.OWNER_ID):
            return bot.reply_to(message, "⚠️ You cannot remove the Owner.")

        deleted = db.del_admin(target_id)
        if deleted:
            bot.reply_to(message, f"🗑️ <b>Removed!</b> User <code>{target_id}</code> is no longer an Admin.")
        else:
            bot.reply_to(message, "❌ <b>Not Found!</b> Ye ID admin list mein nahi hai.")
    except Exception as e:
        bot.reply_to(message, f"❌ <b>Error:</b> {e}")

@bot.message_handler(commands=['admins'])
def list_admins_handler(message):
    if not db.is_admin(message.from_user.id): return
    
    status_msg = bot.reply_to(message, "⏳ <b>Fetching Admin List...</b>")
    admin_ids = db.get_all_admins()
    
    txt = "👮 <b>Bot Admin List:</b>\n\n"
    
    # Owner Info
    try:
        owner_info = bot.get_chat(config.OWNER_ID)
        o_name = html.escape(owner_info.first_name)
        txt += f"👑 <b>Owner:</b> <a href='tg://user?id={config.OWNER_ID}'>{o_name}</a>\n🆔 <code>{config.OWNER_ID}</code>\n\n"
    except:
        txt += f"👑 <b>Owner:</b> ID <code>{config.OWNER_ID}</code>\n\n"

    count = 1
    # Extra Admins Info
    for aid in admin_ids:
        # Skip if ID is owner (Avoid duplicate in list)
        if str(aid) == str(config.OWNER_ID): continue
        # Skip if ID is not numeric (Cleans up your old 'v', 'u' entries)
        if not str(aid).isdigit(): continue
        
        try:
            user = bot.get_chat(aid)
            name = html.escape(user.first_name)
            txt += f"{count}. <a href='tg://user?id={aid}'>{name}</a>\n🆔 <code>{aid}</code>\n\n"
        except:
            txt += f"{count}. <b>User</b>\n🆔 <code>{aid}</code>\n\n"
        count += 1
            
    bot.edit_message_text(txt, message.chat.id, status_msg.message_id)
