### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

import time
import config
import database as db
from bot_instance import bot
from telebot import types

# Temporary storage to track the setup process
TEMP_SLOTS = {}

@bot.message_handler(commands=['add_slot'])
def add_slot_start(message):
    """Initiates the manual slot (filter) addition process"""
    # Security check: Only Admins/Owner can add slots
    if not db.is_admin(message.from_user.id):
        return

    # Extract keyword from command
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(
            message, 
            "⚠️ <b>Usage:</b> <code>/add_slot keyword</code>\n\n"
            "Example: <code>/add_slot my_movie</code>"
        )
    
    keyword = parts[1].lower().strip()
    uid = message.from_user.id
    
    # Initialize the temporary session
    TEMP_SLOTS[uid] = {"kw": keyword}
    
    # Use ForceReply to guide the user
    markup = types.ForceReply(selective=True)
    msg = bot.reply_to(
        message, 
        f"📤 <b>Slot Setup:</b> <code>{keyword}</code>\n\n"
        "Now, send the <b>Message</b> (Text, Photo, Video, or File with Buttons) "
        "that you want to save for this keyword:", 
        reply_markup=markup
    )
    
    # Register the next step to receive the content
    bot.register_next_step_handler(msg, process_slot_content)

def process_slot_content(message):
    uid = message.from_user.id
    
    # Check if the session still exists
    if uid not in TEMP_SLOTS:
        return bot.send_message(message.chat.id, "❌ <b>Session Expired!</b> Please start again.")

    # If user sends another command, cancel the setup
    if message.text and message.text.startswith("/"):
        del TEMP_SLOTS[uid]
        return bot.send_message(uid, "❌ <b>Setup Cancelled.</b>")

    try:
        # Convert DB Channel ID to integer to prevent API errors
        db_channel_id = int(config.DB_CHANNEL_ID)
        
        # 1. FORWARD the message to the DB Channel
        # This is the most stable method to keep Buttons and Media intact
        forwarded = bot.forward_message(
            chat_id=db_channel_id, 
            from_chat_id=message.chat.id, 
            message_id=message.message_id
        )
        
        # 2. SAVE the Post ID to MongoDB
        keyword = TEMP_SLOTS[uid]['kw']
        data = {
            "title": f"Slot: {keyword.title()}",
            "db_mid": int(forwarded.message_id),
            "type": "slot" # Distinguishes manual slots from auto anime filters
        }
        
        db.add_filter(keyword, data)
        
        # 3. Final Success Message
        bot.reply_to(
            message, 
            f"✅ <b>Manual Slot Added Successfully!</b>\n\n"
            f"🏷 <b>Keyword:</b> <code>{keyword}</code>\n"
            f"🆔 <b>Post ID:</b> <code>{forwarded.message_id}</code>\n\n"
            "Now, whenever someone searches for this keyword, the bot will deliver this exact message."
        )
        
        # Clear the session data
        del TEMP_SLOTS[uid]
        
    except Exception as e:
        error_msg = str(e)
        bot.send_message(
            uid, 
            f"❌ <b>Error!</b>\n<code>{error_msg}</code>\n\n"
            f"Ensure the bot is an <b>Admin</b> in the DB Channel: <code>{config.DB_CHANNEL_ID}</code>"
        )
        if uid in TEMP_SLOTS:
            del TEMP_SLOTS[uid]

### Bot by UNRATED CODER --- Support Our Channel @UNRATED_CODER ###
### --------> https://t.me/UNRATED_CODER <-------- ###
