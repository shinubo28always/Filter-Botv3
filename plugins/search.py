import time
from bot_instance import bot
from telebot import types
import database as db
import config
from thefuzz import process

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    # Command check: Agar message / se start ho raha hai toh search skip karo
    if message.text.startswith("/"): 
        return

    uid = message.from_user.id
    db.add_user(uid)
    
    query = message.text.lower().strip()
    
    # FSub Check
    fsub_id = db.get_fsub()
    if fsub_id:
        try:
            status = bot.get_chat_member(fsub_id, uid).status
            if status not in ['member', 'administrator', 'creator']:
                link = bot.create_chat_invite_link(fsub_id).invite_link
                markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✨ Join Channel ✨", url=link))
                return bot.reply_to(message, "<b>❌ Access Denied!</b>\n\nAapne hamara channel join nahi kiya hai. Pehle join karein phir search karein.", reply_markup=markup)
        except Exception as e:
            print(f"FSub Error: {e}")

    # MongoDB se saare keywords nikalna
    choices = db.get_all_keywords()
    if not choices:
        if message.chat.type == "private":
            bot.reply_to(message, "😕 <b>Database abhi khali hai.</b> Admin ko anime add karne kahein.")
        return

    # Fuzzy Matching
    matches = process.extract(query, choices, limit=3)
    best_matches = [m for m in matches if m[1] > 70] # 70% threshold

    if not best_matches:
        if message.chat.type == "private":
            bot.reply_to(message, "❌ <b>Result Nahi Mila!</b>\nSpelling check karein ya /request karein.")
        return

    # Direct Result
    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_res(message, data)
    else:
        # Suggestions
        markup = types.InlineKeyboardMarkup()
        for b in best_matches:
            f_data = db.get_filter(b[0])
            if f_data:
                markup.add(types.InlineKeyboardButton(f_data['title'], callback_data=f"fuz|{b[0]}"))
        bot.reply_to(message, "🧐 <b>Kya aap ye dhund rahe hain?</b>", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz_btn(call):
    key = call.data.split("|")[1]
    data = db.get_filter(key)
    if data:
        send_res(call.message, data, is_cb=True)

def send_res(message, data, is_cb=False):
    target_chat = message.chat.id
    try:
        # Generate 5-min link
        invite = bot.create_chat_invite_link(
            data['source_cid'], 
            expire_date=int(time.time())+300, 
            member_limit=1
        )
        link = invite.invite_link
    except:
        link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    
    try:
        bot.copy_message(
            chat_id=target_chat,
            from_chat_id=config.DB_CHANNEL_ID,
            message_id=data['db_mid'],
            reply_markup=markup,
            message_effect_id=config.EFFECT_PARTY
        )
    except Exception as e:
        bot.send_message(target_chat, f"❌ Error: Result DB channel se delete ho chuka hai.\nID: {data['db_mid']}")

    if is_cb:
        bot.delete_message(target_chat, message.message_id)
