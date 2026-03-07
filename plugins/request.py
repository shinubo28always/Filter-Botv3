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

# --- ADMIN REQUEST MANAGEMENT ---

@bot.message_handler(commands=['requests'])
def list_requests_handler(message):
    if not db.is_admin(message.from_user.id):
        return bot.reply_to(message, config.ROAST_GENERAL, parse_mode="HTML")

    reqs = db.get_pending_requests()
    if not reqs:
        return bot.reply_to(message, "📂 <b>No pending requests!</b>", parse_mode="HTML")

    send_requests_page(message.chat.id, reqs, 1)

def send_requests_page(chat_id, reqs, page, edit_mid=None):
    PER_PAGE = 5
    total_pages = (len(reqs) + PER_PAGE - 1) // PER_PAGE
    start = (page - 1) * PER_PAGE
    page_reqs = reqs[start:start + PER_PAGE]

    txt = f"📝 <b>Pending Requests (Page {page}/{total_pages}):</b>\n\n"
    markup = types.InlineKeyboardMarkup()

    for r in page_reqs:
        q = html.escape(r['query'])
        txt += f"• <b>{q}</b> (From: {html.escape(r['first_name'])})\n"
        markup.add(
            types.InlineKeyboardButton(f"✅ Done: {q[:15]}...", callback_data=f"req_done|{r['uid']}|{r['query'][:20]}")
        )

    nav = []
    if page > 1: nav.append(types.InlineKeyboardButton("⬅️ Back", callback_data=f"req_page|{page-1}"))
    if page < total_pages: nav.append(types.InlineKeyboardButton("Next ➡️", callback_data=f"req_page|{page+1}"))
    if nav: markup.row(*nav)

    if edit_mid:
        try: bot.edit_message_text(txt, chat_id, edit_mid, reply_markup=markup, parse_mode="HTML")
        except: pass
    else:
        bot.send_message(chat_id, txt, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data.startswith(("req_page|", "req_done|")))
def handle_request_management_callbacks(call):
    if not db.is_admin(call.from_user.id): return

    data = call.data.split("|")
    if data[0] == "req_page":
        reqs = db.get_pending_requests()
        send_requests_page(call.message.chat.id, reqs, int(data[1]), edit_mid=call.message.message_id)

    elif data[0] == "req_done":
        # Note: We need the full query for deletion, but callback data is limited in size.
        # For simplicity in this demo, we'll try to find and delete.
        # In a real app, you'd use a unique Request ID.
        uid = data[1]
        short_q = data[2]
        # Fetch all, find matching short query
        reqs = db.get_pending_requests()
        for r in reqs:
            if r['uid'] == uid and r['query'].startswith(short_q):
                db.delete_request(uid, r['query'])
                break

        bot.answer_callback_query(call.id, "✅ Marked as Done!")
        reqs = db.get_pending_requests()
        if reqs:
            send_requests_page(call.message.chat.id, reqs, 1, edit_mid=call.message.message_id)
        else:
            bot.edit_message_text("📂 <b>No pending requests!</b>", call.message.chat.id, call.message.message_id, parse_mode="HTML")

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
