# Please Support Us! @DogeshBhai_Pure_Bot on Telegram! 
# This Bot Created By: @AniReal_Support!
from bot_instance import bot
import config
import database as db
from telebot import types
import html

# --- HELPER FUNCTIONS ---

def send_request_to_admin(message, query):
    uid = message.from_user.id
    first_name = message.from_user.first_name
    
    # 1. Database safety: Agar DB error de toh bhi admin ko msg jaye
    try:
        db.save_request(uid, first_name, query)
    except Exception as e:
        print(f"DB Error: {e}")

    # 2. Admin notification logic
    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("💬 Reply User", callback_data=f"adm_rep|{uid}|{message.message_id}")
    )
    
    # html.escape zaroori hai taaki user ka naam ya query HTML break na kare
    admin_txt = (
        f"📩 <b>New Request!</b>\n\n"
        f"👤 <b>From:</b> {html.escape(first_name)} (<code>{uid}</code>)\n"
        f"📝 <b>Anime:</b> <code>{html.escape(query)}</code>"
    )
    
    try:
        # config.OWNER_ID ko int mein convert karna safe rehta hai
        bot.send_message(int(config.OWNER_ID), admin_txt, reply_markup=markup, parse_mode="HTML")
        bot.reply_to(message, "✅ <b>Your request has been sent!</b>", parse_mode="HTML")
    except Exception as e:
        print(f"Admin Send Error: {e}")
        bot.reply_to(message, "❌ <b>Error:</b> Could not contact Admin. Please try again later.")

# --- COMMAND HANDLERS ---

@bot.message_handler(commands=['request'])
def request_command(message):
    uid = message.from_user.id
    
    # Group check
    if message.chat.type != "private":
        markup = types.InlineKeyboardMarkup()
        bot_username = bot.get_me().username
        markup.add(types.InlineKeyboardButton("📩 Cʟɪᴄᴋ ᴛᴏ Sᴇɴᴅ Rᴇǫᴜᴇsᴛ", url=f"https://t.me/{bot_username}?start=request"))
        
        return bot.reply_to(
            message, 
            "<b>⚠️ Tʜɪs ᴀᴄᴛɪᴏɴ ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ɪɴ ɢʀᴏᴜᴘ ᴄʜᴀᴛs.</b>\n\n✅ 𝑃𝑙𝑒𝑎𝑠𝑒 𝑠𝑤𝑖𝑡𝑐ℎ 𝑡𝑜 𝑃𝑟𝑖𝑣𝑎ᴛ𝑒 𝐶ℎ𝑎𝑡.", 
            reply_markup=markup,
            parse_mode="HTML"
        )
    
    args = message.text.split(maxsplit=1)
    if len(args) == 1:
        instruction = (
          "⚠️ <b>Anime Request Rules:</b>\n\n"
          "To request an anime, use the command followed by the anime name.\n"
          "Usage: <code>/request Naruto Shippuden</code>"
        )
        return bot.reply_to(message, instruction, parse_mode="HTML")
    
    process_request_text(message, args[1])

# --- DEEP LINK & FORCE REPLY LOGIC ---

def initiate_request_flow(uid):
    markup = types.ForceReply(selective=True)
    msg = bot.send_message(
        uid, 
        "<b>👋 Here type your anime request:</b>", 
        reply_markup=markup,
        parse_mode="HTML"
    )
    bot.register_next_step_handler(msg, process_request_text_from_flow)

def process_request_text_from_flow(message):
    if not message.text or message.text.startswith("/"):
        return bot.send_message(message.from_user.id, "❌ Invalid request. Please send a text name.")
    send_request_to_admin(message, message.text)

def process_request_text(message, query):
    send_request_to_admin(message, query)

# --- ADMIN REPLY LOGIC ---

@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_rep|"))
def admin_reply_callback(call):
    data = call.data.split("|")
    target_uid = data[1]
    user_msg_id = data[2]
    
    msg = bot.send_message(call.from_user.id, f"📝 Send reply for <code>{target_uid}</code>:", parse_mode="HTML")
    bot.register_next_step_handler(msg, deliver_reply_to_user, target_uid, user_msg_id)
    bot.answer_callback_query(call.id)

def deliver_reply_to_user(message, target_uid, user_msg_id):
    try:
        reply_text = f"<blockquote><b>Admin Reply:</b>\n\n{html.escape(message.text)}</blockquote>"
        bot.send_message(
            target_uid, 
            reply_text, 
            reply_to_message_id=int(user_msg_id), 
            message_effect_id=getattr(config, 'EFFECT_PARTY', None),
            parse_mode="HTML"
        )
        bot.reply_to(message, "✅ Reply delivered!")
    except Exception:
        # Agar user ne chat delete kar di ho ya msg gayab ho
        bot.send_message(target_uid, f"<blockquote><b>Admin Reply:</b>\n\n{html.escape(message.text)}</blockquote>", parse_mode="HTML")
        bot.reply_to(message, "✅ Original msg missing, normal PM sent.")

# Join & Support Us! @DogeshBhai_Pure_Bot
