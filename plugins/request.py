# Please Support Us! @DogeshBhai_Pure_Bot on Telegram! 
# This Bot Created By: @AniReal_Support!
from bot_instance import bot
import config
import database as db
from telebot import types, apihelper
import html

@bot.message_handler(commands=['request'])
def request_command(message):
    uid = message.from_user.id
    
    # GC REDIRECT: Redirect to PM without needing /request again
    if message.chat.type != "private":
        markup = types.InlineKeyboardMarkup()
        bot_username = bot.get_me().username
        # Deep Link: start=request
        markup.add(types.InlineKeyboardButton("🚀 Request in PM", url=f"https://t.me/{bot_username}?start=request"))
        
        return bot.reply_to(
            message, 
            "<b>⚠️ Tʜɪs ᴀᴄᴛɪᴏɴ ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ɪɴ ɢʀᴏᴜᴘ ᴄʜᴀᴛs.</b>\n\n✅ 𝑃𝑙𝑒𝑎𝑠𝑒 𝑠𝑤𝑖𝑡𝑐ℎ 𝑡𝑜 𝑃𝑟𝑖𝑣𝑎𝑡𝑒 𝐶ℎ𝑎𝑡 𝑢𝑠𝑖𝑛𝑔 𝑡ℎ𝑒 𝑏𝑢𝑡𝑡𝑜𝑛 𝑏𝑒𝑙𝑜𝑤. 🔰", 
            reply_markup=markup
        )
    
    # PM DIRECT COMMAND: Send instruction manual
    args = message.text.split(maxsplit=1)
    if len(args) == 1:
# Please Support Us! @DogeshBhai_Pure_Bot on Telegram! 
# This Bot Created By: @AniReal_Support!
        instruction = (
            "⚠️ <b>Anime Request Rules:</b>\n\n"
            "Request karne ke liye command ke saath anime ka naam likhein.\n"
            "Usage: <code>/request Naruto Shippuden</code>"
        )
        return bot.reply_to(message, instruction)
    
    # PM WITH ARGS: Process request
    process_request_text(message, args[1])

def initiate_request_flow(uid):
    """Deep link se click karne par direct Force Reply aayega"""
    markup = types.ForceReply(selective=True)
    msg = bot.send_message(
        uid, 
        "<b>👋 Here type your anime request:</b>\n\nMain aapki request Admin tak pahuncha dunga.", 
        reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_request_text_from_flow)

def process_request_text_from_flow(message):
    """Force reply ka result process karne ke liye"""
    if not message.text or message.text.startswith("/"):
        return bot.send_message(message.from_user.id, "❌ Invalid request.")
    send_request_to_admin(message, message.text)

def process_request_text(message, query):
    """Direct /request [name] command process karne ke liye"""
    send_request_to_admin(message, query)

def send_request_to_admin(message, query):
    uid = message.from_user.id
    db.save_request(uid, message.from_user.first_name, query)
    
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("💬 Reply User", callback_data=f"adm_rep|{uid}|{message.message_id}")
    )
    admin_txt = f"📩 <b>New Request!</b>\n👤 From: {message.from_user.first_name} (<code>{uid}</code>)\n📝 Anime: <code>{query}</code>"
    bot.send_message(config.OWNER_ID, admin_txt, reply_markup=markup)
    bot.reply_to(message, "✅ <b>Your request has been sent!</b>")

# Admin Reply handler same rahega...
@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_rep|"))
def admin_reply_callback(call):
    _, target_uid, user_msg_id = call.data.split("|")
    msg = bot.send_message(call.from_user.id, f"📝 Send reply for <code>{target_uid}</code>:")
    bot.register_next_step_handler(msg, deliver_reply_to_user, target_uid, user_msg_id)

def deliver_reply_to_user(message, target_uid, user_msg_id):
    try:
        bot.send_message(target_uid, f"<blockquote><b>Admin Reply:</b>\n\n{message.text}</blockquote>", 
                         reply_to_message_id=int(user_msg_id), message_effect_id=config.EFFECT_PARTY)
        bot.reply_to(message, "✅ Reply delivered!")
    except:
        bot.send_message(target_uid, f"<blockquote><b>Admin Reply:</b>\n\n{message.text}</blockquote>")
        bot.reply_to(message, "✅ Original msg missing, normal PM sent.")
# Join & Support Us! @DogeshBhai_Pure_Bot
