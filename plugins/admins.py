# Please Support Us! @DogeshBhai_Pure_Bot on Telegram! 
# This Bot Created By: @AniReal_Support!
import os
from bot_instance import bot
import config, time
import database as db
from telebot import types
import html, json, io

@bot.message_handler(commands=['add_admin'])
def add_admin_handler(message):
    # Only Owner can add
    if str(message.from_user.id) != str(config.OWNER_ID):
        return bot.reply_to(message, "❌ <b>Only Owner can use this!</b>")
    
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
            return bot.reply_to(message, "❌ <b>User Not Found!</b>\n⚠️ Possibly the user hasn’t started the bot yet or has blocked it.")

        # 3. Try to notify the new Admin
        owner_name = html.escape(message.from_user.first_name)
        owner_id = message.from_user.id
        owner_mention = f"<a href='tg://user?id={owner_id}'>{owner_name}</a>"

        try:
            notification_text = (
             "🎉 <b>Congratulations!</b>\n\n"
            f"{owner_mention} has made you an <b>Admin</b> of this bot.\n"
             "You can now manage filters and channels."
          )
            bot.send_message(target_id, notification_text)
        except Exception as e:
            return bot.reply_to(message, f"❌ <b>Error:</b> {e}")

        # 4. Final Save to DB
        db.add_admin(target_id)
        bot.reply_to(message, f"✅ <b>Success!</b>\nUser <code>{target_id}</code> is now an Admin and has been notified.")

    except Exception as e:
        bot.reply_to(message, f"❌ <b>Critical Error:</b> {e}")

@bot.message_handler(commands=['ban'])
def ban_user_handler(message):
    if not db.is_admin(message.from_user.id):
        return bot.reply_to(message, config.ROAST_BROADCAST_BAN, parse_mode="HTML")
    parts = message.text.split()
    if len(parts) < 2: return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/ban user_id</code>")
    uid = parts[1]
    db.ban_user(uid)
    bot.reply_to(message, f"🚫 <b>User Banned:</b> <code>{uid}</code>")

@bot.message_handler(commands=['unban'])
def unban_user_handler(message):
    if not db.is_admin(message.from_user.id):
        return bot.reply_to(message, config.ROAST_BROADCAST_BAN, parse_mode="HTML")
    parts = message.text.split()
    if len(parts) < 2: return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/unban user_id</code>")
    uid = parts[1]
    if db.unban_user(uid):
        bot.reply_to(message, f"✅ <b>User Unbanned:</b> <code>{uid}</code>")
    else:
        bot.reply_to(message, "❌ <b>User not found in ban list.</b>")

@bot.message_handler(commands=['restart'])
def restart_bot(message):
    if str(message.from_user.id) != str(config.OWNER_ID): return
    bot.reply_to(message, "🔄 <b>Bot is restarting...</b>", parse_mode="HTML")
    time.sleep(2)
    os._exit(0)

@bot.message_handler(commands=['del_admin'])
def del_admin_handler(message):
    if str(message.from_user.id) != str(config.OWNER_ID):
        return bot.reply_to(message, "❌ <b>Only Owner can remove admins!</b>")
    
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
            bot.reply_to(message, "❌ <b>Not Found!</b> This ID is not in the admin list.")
    except Exception as e:
        bot.reply_to(message, f"❌ <b>Error:</b> {e}")

@bot.message_handler(commands=['maintenance'])
def toggle_maintenance(message):
    if not db.is_admin(message.from_user.id):
        return bot.reply_to(message, config.ROAST_GENERAL, parse_mode="HTML")

    curr = db.get_maintenance()
    new_status = not curr
    db.set_maintenance(new_status)

    txt = "🛠 <b>Maintenance Mode:</b> " + ("<code>ENABLED</code>" if new_status else "<code>DISABLED</code>")
    bot.reply_to(message, txt, parse_mode="HTML")

@bot.message_handler(commands=['backup'])
def backup_database(message):
    if not db.is_admin(message.from_user.id):
        return bot.reply_to(message, config.ROAST_GENERAL, parse_mode="HTML")

    msg = bot.reply_to(message, "📤 <b>Generating Filter Backup...</b>")

    try:
        filters_data = db.get_all_filters_list()
        # Full data nikalein details ke saath
        full_filters = []
        for f in filters_data:
            details = db.get_filter(f['keyword'])
            if details:
                # MongoDB object IDs are not JSON serializable easily
                if '_id' in details: del details['_id']
                full_filters.append(details)

        json_data = json.dumps(full_filters, indent=4)
        bio = io.BytesIO(json_data.encode())
        bio.name = f"filters_backup_{int(time.time())}.json"

        bot.send_document(message.chat.id, bio, caption=f"✅ <b>Backup Successful!</b>\nTotal Filters: <code>{len(full_filters)}</code>", parse_mode="HTML")
        bot.delete_message(message.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ <b>Backup Failed:</b>\n<code>{e}</code>", message.chat.id, msg.message_id)

@bot.message_handler(commands=['admins'])
def list_admins_handler(message):
    if not db.is_admin(message.from_user.id):
        return bot.reply_to(message, config.ROAST_GENERAL, parse_mode="HTML")
    
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


# Please Support Us! @DogeshBhai_Pure_Bot on Telegram! 
# This Bot Created By: @AniReal_Support!
# Join & Support Us! @DogeshBhai_Pure_Bot
