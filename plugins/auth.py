# Please Support Us! @UNRATED_CODER on Telegram! 
# This Bot Created By: @UNRATED_CODER!
import html
from bot_instance import bot
import database as db
import config
from telebot import types

@bot.my_chat_member_handler()
def handle_membership_security(message):
    new = message.new_chat_member
    chat = message.chat
    
    # Inviter detecting 
    inviter_id = message.from_user.id if message.from_user else None

    # --- CHANNEL PROTECTION ---
    if chat.type == "channel":
        if new.status == "administrator":
            # Security Check
            if inviter_id and db.is_admin(inviter_id):
                # Channel title ko clean karna
                safe_title = html.escape(chat.title)
                
                # Format: setup|chat_id
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("➕ Add Filter", callback_data=f"setup|{chat.id}")
                )
                
                txt = (
                    f"✅ <b>Channel Authorized!</b>\n\n"
                    f"Channel: <b>{safe_title}</b>\n"
                    f"ID: <code>{chat.id}</code>\n\n"
                    f"Aap niche button se is channel ke anime filters add kar sakte hain."
                )
                
                try:
                    bot.send_message(inviter_id, txt, reply_markup=markup, parse_mode='HTML')
                except:
                    # Fallback to Owner
                    try:
                        bot.send_message(
                            config.OWNER_ID, 
                            f"📢 <b>Authorized:</b> {safe_title}\nID: <code>{chat.id}</code>", 
                            reply_markup=markup, 
                            parse_mode='HTML'
                        )
                    except: pass
            else:
                # Unauthorized user: Leave
                try: bot.leave_chat(chat.id)
                except: pass

 # Please Support Us! @UNRATED_CODER on Telegram! 
 # This Bot Created By: @UNRATED_CODER!

    # --- GROUP TRACKING ---
    elif chat.type in ["group", "supergroup"]:
    if new.status in ["administrator", "member"]:
        db.add_group(chat.id, chat.title)
    elif new.status in ["left", "kicked"]:
        db.del_group(chat.id)

@bot.message_handler(content_types=['new_chat_members'])
def on_join_group(message):
    for user in message.new_chat_members:
        if user.id == bot.get_me().id:
            # DB update
            db.add_group(message.chat.id, message.chat.title)

            # GROUP_AUTH_MSG from config
            # Safe logic for clickable group name
            chat_name = message.chat.title
            chat_link = None

            try:
                # Check if chat is public or bot can get invite link
                if message.chat.username:
                    # Public group → t.me link
                    chat_link = f"https://t.me/{message.chat.username}"
                else:
                    # Try to get invite link if bot is admin
                    chat_info = bot.get_chat(message.chat.id)
                    if chat_info.invite_link:
                        chat_link = chat_info.invite_link
            except Exception:
                chat_link = None  # fallback

            # Prepare message
            if chat_link:
                # clickable name
                group_text = f"<a href='{chat_link}'>{chat_name}</a>"
            else:
                # just text
                group_text = f"<b>{chat_name}</b>"

            # Send message from config
            msg_text = config.GROUP_AUTH_MSG.format(group_name=group_text)
            bot.send_message(message.chat.id, msg_text, parse_mode="HTML")

# Join & Support Us! @UNRATED_CODER!
