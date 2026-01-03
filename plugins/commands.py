import time
import os
import html
from bot_instance import bot
import config
import database as db
from telebot import types

@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    first_name = html.escape(message.from_user.first_name)
    
    # 1. Register User Always
    db.add_user(uid)
    
    # 2. STRICT FSUB CHECK (PM ONLY)
    if message.chat.type == "private":
        fsub_channels = db.get_all_fsub()
        for f in fsub_channels:
            f_id = int(f['_id'])
            try:
                # Check User Membership
                member = bot.get_chat_member(f_id, uid)
                if member.status not in ['member', 'administrator', 'creator']:
                    raise Exception("NotJoined")
            except Exception as e:
                # ERROR HANDLING: Agar user join nahi hai ya bot admin nahi hai
                err_msg = str(e)
                markup = types.InlineKeyboardMarkup()
                
                if "NotJoined" in err_msg or "user not found" in err_msg.lower():
                    # Jab user ne join nahi kiya
                    final_txt = f"👋 <b>Welcome {first_name}!</b>\n\nBot use karne ke liye hamara channel <b>{f['title']}</b> join karein."
                    try:
                        is_req = f.get('mode') == "request"
                        expiry = 300 if is_req else 120
                        invite = bot.create_chat_invite_link(f_id, expire_date=int(time.time()) + expiry, creates_join_request=is_req, member_limit=1)
                        markup.add(types.InlineKeyboardButton("✨ Jᴏɪɴ Cʜᴀɴɴᴇʟ ✨", url=invite.invite_link))
                    except:
                        # Fallback if link generation fails (Bot not admin)
                        final_txt += "\n\n⚠️ <i>Error: Bot is not Admin in FSub Channel!</i>"
                else:
                    # Koi aur technical error (Like Bot not admin)
                    final_txt = f"❌ <b>FSub Access Error!</b>\n\nBot ko channel <b>{f['title']}</b> mein access nahi mil raha.\n\n<code>Error: {err_msg}</code>"
                
                markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))
                return bot.reply_to(message, final_txt, reply_markup=markup, parse_mode='HTML')

    # 3. HANDLE DEEP LINKING (If user comes from /request button)
    if message.chat.type == "private" and len(message.text.split()) > 1:
        if message.text.split()[1] == "request":
            try:
                from plugins.request import initiate_request_flow
                return initiate_request_flow(uid)
            except: pass

    # 4. STICKER ANIMATION (Only if FSub passed)
    try:
        stk = bot.send_sticker(chat_id, config.STICKER_ID)
        time.sleep(1.2)
        bot.delete_message(chat_id, stk.message_id)
    except: pass

    # 5. START MESSAGE DELIVERY
    if message.chat.type == "private":
        pm_text = config.PM_START_MSG.format(first_name=first_name)
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✨ Jᴏɪɴ Uᴘᴅᴀᴛᴇs ✨", url=config.LINK_ANIME_CHANNEL))
        markup.add(types.InlineKeyboardButton("➕ Aᴅᴅ Bᴏᴛ ᴛᴏ Gʀᴏᴜᴘ ➕", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
        
        try:
            bot.send_photo(chat_id, config.START_IMG, caption=pm_text, reply_markup=markup, parse_mode='HTML', message_effect_id=config.EFFECT_FIRE)
        except:
            bot.send_message(chat_id, pm_text, reply_markup=markup, parse_mode='HTML', message_effect_id=config.EFFECT_FIRE)
    else:
        # Group Start Logic
        group_name = html.escape(message.chat.title)
        group_text = config.GROUP_START_MSG.format(group_name=group_name)
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🤖 PM Mᴇ", url=f"https://t.me/{bot.get_me().username}?start=help"))
        bot.send_message(chat_id, group_text, reply_markup=markup, parse_mode='HTML')

# ==========================================
# 👇 OTHER COMMANDS (PING, STATS, FILTERS, DEL)
# ==========================================

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    start = time.time()
    msg = bot.reply_to(message, "⚡")
    ms = round((time.time() - start) * 1000)
    bot.edit_message_text(f"📶 <b>Pong:</b> <code>{ms}ms</code>", message.chat.id, msg.message_id, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not db.is_admin(message.from_user.id): return
    u = len(db.get_all_users())
    f = len(db.get_all_filters_list())
    bot.reply_to(message, f"📊 <b>Stats:</b>\nUsers: <code>{u}</code>\nFilters: <code>{f}</code>", parse_mode='HTML')

@bot.message_handler(commands=['filters'])
def list_filters(message):
    if not db.is_admin(message.from_user.id): return
    fs = db.get_all_filters_list()
    if not fs: return bot.reply_to(message, "📂 Database Khali!")
    txt = "📂 <b>Filters:</b>\n\n" + "\n".join([f"• <code>{x['keyword']}</code>" for x in fs])
    bot.reply_to(message, txt[:4000], parse_mode='HTML')

@bot.message_handler(commands=['del_filter'])
def delete_filter_cmd(message):
    if not db.is_admin(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: return bot.reply_to(message, "⚠️ Usage: /del_filter name")
    target = parts[1].lower().strip()
    
    if target == "all":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ Confirm All", callback_data="hard_del_all_filters"))
        return bot.reply_to(message, "⚠️ Delete all filters?", reply_markup=markup)
    
    if db.delete_filter(target):
        bot.reply_to(message, f"🗑️ Deleted: <code>{target}</code>", parse_mode='HTML')
    else:
        bot.reply_to(message, "❌ Filter nahi mila.")

@bot.callback_query_handler(func=lambda call: call.data == "hard_del_all_filters")
def handle_del_all(call):
    if not db.is_admin(call.from_user.id): return
    db.delete_all_filters()
    bot.edit_message_text("🗑️ <b>All filters deleted!</b>", call.message.chat.id, call.message.message_id, parse_mode='HTML')
