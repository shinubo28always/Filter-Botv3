from bot_instance import bot
import config
import database as db
from telebot import types
import html

@bot.message_handler(commands=['add_admin'])
def add_admin_handler(message):
    # Strict Check: Sirf Main Owner hi add kar sakta hai
    if str(message.from_user.id) != str(config.OWNER_ID):
        return bot.reply_to(message, "❌ <b>Only the Main Owner can add new admins!</b>")
    
    try:
        # Command format: /add_admin 12345678
        parts = message.text.split()
        if len(parts) < 2:
            return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/add_admin USER_ID</code>")
        
        new_admin_id = parts[1].strip()
        db.add_admin(new_admin_id)
        bot.reply_to(message, f"✅ <b>Success!</b> User <code>{new_admin_id}</code> is now an Admin.")
    except Exception as e:
        bot.reply_to(message, f"❌ <b>Error:</b> {e}")

@bot.message_handler(commands=['del_admin'])
def del_admin_handler(message):
    # Strict Check: Sirf Main Owner hi delete kar sakta hai
    if str(message.from_user.id) != str(config.OWNER_ID):
        return bot.reply_to(message, "❌ <b>Only the Main Owner can remove admins!</b>")
    
    try:
        parts = message.text.split()
        if len(parts) < 2:
            return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/del_admin USER_ID</code>")
        
        target_id = parts[1].strip()
        
        if target_id == str(config.OWNER_ID):
            return bot.reply_to(message, "⚠️ <b>Baka!</b> You cannot remove yourself.")

        deleted = db.del_admin(target_id)
        if deleted:
            bot.reply_to(message, f"🗑️ <b>Removed!</b> User <code>{target_id}</code> is no longer an Admin.")
        else:
            bot.reply_to(message, "❌ User not found in Admin list.")
    except Exception as e:
        bot.reply_to(message, f"❌ <b>Error:</b> {e}")

@bot.message_handler(commands=['admins'])
def list_admins_handler(message):
    # Check if requester is Admin or Owner
    if not db.is_admin(message.from_user.id):
        return
    
    # Status message
    status_msg = bot.reply_to(message, "⏳ <b>Fetching Admin List...</b>")
    
    admin_ids = db.get_all_admins()
    
    # Header
    txt = "👮 <b>Bot Admin List:</b>\n\n"
    
    # 1. Main Owner ko top par rakhein
    try:
        owner_info = bot.get_chat(config.OWNER_ID)
        owner_name = html.escape(owner_info.first_name)
        txt += f"👑 <b>Owner:</b> <a href='tg://user?id={config.OWNER_ID}'>{owner_name}</a>\n🆔 <code>{config.OWNER_ID}</code>\n\n"
    except:
        txt += f"👑 <b>Owner:</b> <i>(Hidden)</i>\n🆔 <code>{config.OWNER_ID}</code>\n\n"

    # 2. Baki Admins ko list karein
    count = 1
    if not admin_ids:
        txt += "📂 <i>No extra admins added.</i>"
    else:
        for aid in admin_ids:
            if str(aid) == str(config.OWNER_ID): continue # Skip owner if already in DB
            try:
                user = bot.get_chat(aid)
                name = html.escape(user.first_name)
                # Mention link + ID
                txt += f"{count}. <a href='tg://user?id={aid}'>{name}</a>\n🆔 <code>{aid}</code>\n\n"
            except:
                txt += f"{count}. <b>User</b>\n🆔 <code>{aid}</code>\n\n"
            count += 1
            
    bot.edit_message_text(txt, message.chat.id, status_msg.message_id)
