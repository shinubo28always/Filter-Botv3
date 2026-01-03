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
    group_name = html.escape(message.chat.title) if message.chat.title else "this group"
    
    # Register user in DB
    db.add_user(uid)
    
    # --- 1. STRICT FSUB CHECK (FOR EVERYONE - NO EXCEPTIONS) ---
    if message.chat.type == "private":
        fsub_channels = db.get_all_fsub()
        for f in fsub_channels:
            try:
                # Force Integer ID check
                f_id = int(f['_id'])
                member = bot.get_chat_member(f_id, uid)
                
                # Check if user is not in channel
                if member.status not in ['member', 'administrator', 'creator']:
                    raise Exception("Not Joined")
                    
            except Exception as e:
                # Yahan koi bhi error aaye (Not Joined ya Bot Error), user ko dikhayega
                err_text = str(e)
                markup = types.InlineKeyboardMarkup()
                
                if "Not Joined" in err_text or "user not found" in err_text.lower():
                    msg_txt = f"👋 <b>Welcome {first_name}!</b>\n\nBot use karne ke liye hamara channel <b>{f['title']}</b> join karein."
                    try:
                        is_req = f.get('mode') == "request"
                        expiry = 300 if is_req else 120
                        invite = bot.create_chat_invite_link(f_id, expire_date=int(time.time()) + expiry, creates_join_request=is_req, member_limit=1)
                        btn_txt = "✨ ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ ✨" if is_req else "✨ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ✨"
                        markup.add(types.InlineKeyboardButton(btn_txt, url=invite.invite_link))
                    except Exception as invite_err:
                        print(f"Invite Link Error: {invite_err}")
                else:
                    # Agar bot admin nahi hai ya koi aur technical error hai
                    msg_txt = f"❌ <b>FSub Error!</b>\n\n<code>{err_text}</code>\n\nAdmin ko report karein."
                
                markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))
                
                # Return karke execution rok dena (User aage nahi badh payega)
                return bot.reply_to(message, msg_txt, reply_markup=markup, parse_mode='HTML')

    # --- 2. DEEP LINKING (REQUEST) ---
    if message.chat.type == "private" and len(message.text.split()) > 1:
        if message.text.split()[1] == "request":
            from plugins.request import initiate_request_flow
            initiate_request_flow(uid)
            return

    # --- 3. STICKER ANIMATION (Common for both) ---
    try:
        stk = bot.send_sticker(chat_id, config.STICKER_ID)
        time.sleep(1.2)
        bot.delete_message(chat_id, stk.message_id)
    except: pass

    # --- 4. START MESSAGE DELIVERY ---
    if message.chat.type == "private":
        # PM Start logic
        pm_text = config.PM_START_MSG.format(first_name=first_name)
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✨ Join Updates ✨", url=config.LINK_ANIME_CHANNEL))
        markup.add(types.InlineKeyboardButton("➕ Add Bot to Group ➕", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
        
        try:
            bot.send_photo(chat_id, config.START_IMG, caption=pm_text, reply_markup=markup, parse_mode='HTML', message_effect_id=config.EFFECT_FIRE)
        except:
            bot.send_message(chat_id, pm_text, reply_markup=markup, parse_mode='HTML', message_effect_id=config.EFFECT_FIRE)
    else:
        # Group Start logic
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
