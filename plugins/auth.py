from bot_instance import bot
import database as db
import config
from telebot import types

# --- 1. CHANNEL SECURITY & SETUP INITIATION ---
@bot.my_chat_member_handler()
def handle_bot_membership(message):
    new_status = message.new_chat_member.status
    chat_type = message.chat.type
    user_id = message.from_user.id # Jisne bot ko add kiya

    # Agar bot kisi CHANNEL mein add hua hai
    if chat_type == "channel":
        if new_status in ['administrator', 'member']:
            # Security: Check if added by Owner or Authorized Admin
            if not db.is_admin(user_id):
                bot.leave_chat(message.chat.id)
                print(f"DEBUG: Unauthorized channel {message.chat.title} detected. Leaved.")
            else:
                # Sirf authorized person ke liye setup button PM mein bhejna
                markup = types.InlineKeyboardMarkup().add(
                    types.InlineKeyboardButton("➕ Add Filter", callback_data=f"setup|{message.chat.id}|{message.chat.title}")
                )
                bot.send_message(
                    config.OWNER_ID, 
                    f"📢 <b>Channel Authorized!</b>\n\nName: {message.chat.title}\nID: <code>{message.chat.id}</code>\nAdded by: <code>{user_id}</code>", 
                    reply_markup=markup
                )

    # Agar bot kisi GROUP mein add/remove hua hai (For Broadcast tracking)
    elif chat_type in ["group", "supergroup"]:
        if new_status in ['administrator', 'member']:
            db.add_group(message.chat.id, message.chat.title)
            print(f"DEBUG: Group {message.chat.title} added to database.")
        elif new_status in ['left', 'kicked']:
            db.remove_group(message.chat.id)
            print(f"DEBUG: Group {message.chat.id} removed from database.")

# --- 2. NEW MEMBER HANDLER (FOR GROUPS) ---
# Jab bot kisi naye group mein join karta hai tab welcome message
@bot.message_handler(content_types=['new_chat_members'])
def on_group_join(message):
    for user in message.new_chat_members:
        if user.id == bot.get_me().id:
            # Group ko DB mein save karein
            db.add_group(message.chat.id, message.chat.title)
            
            markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("📢 Updates", url=config.LINK_ANIME_CHANNEL)
            )
            bot.send_message(
                message.chat.id, 
                "👋 <b>Hello Everyone!</b>\n\nI am an Advanced Anime Filter Bot. Just type your favorite anime name to get links.\n\n<b>Join our updates channel for more!</b>", 
                reply_markup=markup
            )
