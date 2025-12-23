from bot_instance import bot
import config
import database as db
from telebot import types, apihelper
import html

# --- REQUEST HANDLER ---
@bot.message_handler(commands=['request'])
def request_command(message):
    uid = message.from_user.id
    
    # 1. Agar Group mein command diya jaye
    if message.chat.type != "private":
        markup = types.InlineKeyboardMarkup()
        # Deep link URL: bot_username?start=request
        bot_username = bot.get_me().username
        markup.add(types.InlineKeyboardButton("🚀 Request in PM", url=f"https://t.me/{bot_username}?start=request"))
        
        return bot.reply_to(
            message, 
            "<b>❌ Request feature sirf PM (Private Chat) mein kaam karta hai!</b>\n\nNiche button par click karke PM mein request karein.", 
            reply_markup=markup
        )
    
    # 2. Agar PM mein command diya jaye
    initiate_request_flow(uid)

def initiate_request_flow(uid):
    """User ko Force Reply ke saath request pucha jayega"""
    markup = types.ForceReply(selective=True)
    msg = bot.send_message(
        uid, 
        "<b>👋 Here type your anime request:</b>\n\n(Example: Naruto Shippuden Season 1 Hindi Dub)", 
        reply_markup=markup
    )
    # Register next step
    bot.register_next_step_handler(msg, process_request_text)

def process_request_text(message):
    uid = message.from_user.id
    query = message.text
    
    if not query or query.startswith("/"):
        return bot.send_message(uid, "⚠️ Request cancel kar di gayi hai.")

    # MongoDB mein request save karna (msg_id ke saath tracking ke liye)
    db.save_request(uid, message.from_user.first_name, query)
    
    # Admin ko notify karna
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("💬 Reply User", callback_data=f"adm_rep|{uid}|{message.message_id}")
    )
    
    admin_txt = (
        f"📩 <b>New Anime Request!</b>\n\n"
        f"👤 <b>From:</b> {html.escape(message.from_user.first_name)} (<code>{uid}</code>)\n"
        f"📝 <b>Anime:</b> <code>{html.escape(query)}</code>"
    )
    bot.send_message(config.OWNER_ID, admin_txt, reply_markup=markup)
    
    bot.reply_to(message, "✅ <b>Your request has been sent to Admin!</b>\nMain aapko notify kar dunga.")

# --- ADMIN REPLY HANDLER ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_rep|"))
def admin_reply_callback(call):
    _, target_uid, user_msg_id = call.data.split("|")
    
    msg = bot.send_message(call.from_user.id, f"📝 Send your reply for user <code>{target_uid}</code>:")
    bot.register_next_step_handler(msg, deliver_reply_to_user, target_uid, user_msg_id)

def deliver_reply_to_user(message, target_uid, user_msg_id):
    admin_text = f"<blockquote><b>Admin Reply:</b>\n\n{message.text}</blockquote>"
    
    try:
        # 1. Koshish karein ki user ke original message par reply jaye
        bot.send_message(
            target_uid, 
            admin_text, 
            reply_to_message_id=int(user_msg_id),
            message_effect_id=config.EFFECT_PARTY
        )
        bot.reply_to(message, "✅ Reply delivered as a reply to request!")
        
    except apihelper.ApiTelegramException as e:
        # 2. Agar user ne msg dlt kar diya (Error 400)
        if "message to be replied not found" in e.description.lower():
            try:
                bot.send_message(target_uid, admin_text)
                bot.reply_to(message, "⚠️ Original msg deleted, reply sent as normal PM.")
            except:
                bot.reply_to(message, "❌ User has blocked the bot!")
        
        # 3. Agar user ne bot block kar diya (Error 403)
        elif e.error_code == 403:
            bot.reply_to(message, "❌ Failed! User ne bot ko block kar diya hai.")
        else:
            bot.reply_to(message, f"❌ Error: {e.description}")
