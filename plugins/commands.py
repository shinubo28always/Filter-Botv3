### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

import time
import os
import io
import html
from bot_instance import bot
import config
import database as db
from telebot import types

# ================= START COMMAND WITH BUTTON LOGIC ==================
@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    first_name = html.escape(message.from_user.first_name)
    group_name = html.escape(message.chat.title) if message.chat.title else "this group"

    # User register
    db.add_user(uid)

    # --- Handle deep linking (request) ---
    if message.chat.type == "private" and len(message.text.split()) > 1:
        if message.text.split()[1] == "request":
            try:
                from plugins.request import initiate_request_flow
                return initiate_request_flow(uid)
            except:
                pass

    # --- Sticker animation ---
    try:
        stk = bot.send_sticker(chat_id, config.STICKER_ID)
        time.sleep(1.2)
        bot.delete_message(chat_id, stk.message_id)
    except:
        pass

    # --- Start Message PM vs Group ---
    if message.chat.type == "private":
        pm_text = config.PM_START_MSG.format(first_name=first_name)

        # Inline keyboard
        markup = types.InlineKeyboardMarkup()
        # Row 1: Join Updates
        markup.row(types.InlineKeyboardButton("✨ Join Updates ✨", url=config.LINK_ANIME_CHANNEL))
        # Row 2: Help | About
        markup.row(
            types.InlineKeyboardButton("📖 Help", callback_data="start_help"),
            types.InlineKeyboardButton("ℹ️ About", callback_data="start_about")
        )
        # Row 3: Add Bot to Group
        markup.row(types.InlineKeyboardButton("➕ Add Bot to Group ➕", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))

        try:
            bot.send_photo(
                chat_id,
                config.START_IMG,
                caption=pm_text,
                reply_markup=markup,
                parse_mode='HTML',
                message_effect_id=config.EFFECT_FIRE
            )
        except:
            bot.send_message(
                chat_id,
                pm_text,
                reply_markup=markup,
                parse_mode='HTML',
                message_effect_id=config.EFFECT_FIRE
            )
    else:
        # Group start message
        group_text = config.GROUP_START_MSG.format(group_name=group_name)
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🤖 PM Me", url=f"https://t.me/{bot.get_me().username}?start=help")
        )
        try:
            bot.reply_to(message, group_text, reply_markup=markup, parse_mode='HTML')
        except:
            bot.send_message(chat_id, group_text, reply_markup=markup, parse_mode='HTML')


# ================= CALLBACK HANDLER FOR HELP/ABOUT/BACK ==================
@bot.callback_query_handler(func=lambda call: call.data in ["start_help", "start_about", "start_back"])
def start_callback(call):
    uid = call.from_user.id
    chat_id = call.message.chat.id

    if call.data == "start_help":
        text = config.HELP_MSG
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("⬅️ Back", callback_data="start_back"),
            types.InlineKeyboardButton("ℹ️ About", callback_data="start_about")
        )
        bot.edit_message_caption(
            chat_id, call.message.message_id,
            caption=text, reply_markup=markup, parse_mode='HTML'
        )
    elif call.data == "start_about":
        text = config.ABOUT_MSG
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("⬅️ Back", callback_data="start_back"),
            types.InlineKeyboardButton("📖 Help", callback_data="start_help")
        )
        bot.edit_message_caption(
            chat_id, call.message.message_id,
            caption=text, reply_markup=markup, parse_mode='HTML'
        )
    elif call.data == "start_back":
        first_name = html.escape(call.from_user.first_name)
        pm_text = config.PM_START_MSG.format(first_name=first_name)
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✨ Join Updates ✨", url=config.LINK_ANIME_CHANNEL))
        markup.row(
            types.InlineKeyboardButton("📖 Help", callback_data="start_help"),
            types.InlineKeyboardButton("ℹ️ About", callback_data="start_about")
        )
        markup.row(types.InlineKeyboardButton("➕ Add Bot to Group ➕", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
        bot.edit_message_caption(
            chat_id, call.message.message_id,
            caption=pm_text, reply_markup=markup, parse_mode='HTML'
        )

# ==========================================
# 👇 ADMIN COMMANDS
# ==========================================

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    s = time.time()
    msg = bot.reply_to(message, "⚡")
    bot.edit_message_text(f"📶 <b>Pong:</b> <code>{round((time.time()-s)*1000)}ms</code>", message.chat.id, msg.message_id, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not db.is_admin(message.from_user.id): return
    u_count = len(db.get_all_users())
    f_count = len(db.get_all_filters_list())
    bot.reply_to(message, f"📊 <b>Bot Statistics:</b>\n\n👤 Users: <code>{u_count}</code>\n📂 Filters: <code>{f_count}</code>", parse_mode='HTML')

@bot.message_handler(commands=['filters'])
def list_filters(message):
    """Aapka Updated Filters Logic (Short msg vs Large file)"""
    if not db.is_admin(message.from_user.id):
        return

    fs = db.get_all_filters_list()
    if not fs:
        return bot.reply_to(message, "📂 <b>Database is empty!</b>")

    lines = [str(x['keyword']) for x in fs]
    full_text = "\n".join(lines)

    # ---------- CASE 1: SHORT LIST (SEND MESSAGE) ----------
    if len(full_text) <= 3800:
        safe_lines = [f"• <code>{html.escape(k)}</code>" for k in lines]
        txt = "📂 <b>Available Filters:</b>\n\n" + "\n".join(safe_lines)
        return bot.reply_to(message, txt, parse_mode="HTML")

    # ---------- CASE 2: LARGE LIST (SEND FILE) ----------
    file_content = "AVAILABLE FILTERS IN ANI-REAL BOT\n\n" + full_text
    file = io.BytesIO(file_content.encode("utf-8"))
    file.name = "filters_list.txt"

    bot.send_document(
        message.chat.id,
        file,
        caption="📂 <b>Too many filters to display.</b>\nHere is the full list as a file.",
        parse_mode="HTML"
    )

@bot.message_handler(commands=['del_filter'])
def delete_filter_cmd(message):
    if not db.is_admin(message.from_user.id): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/del_filter name</code>")
    
    target = parts[1].lower().strip()
    
    if target == "all":
        # Specific filter named 'all' check
        if db.get_filter("all"):
            db.delete_filter("all")
            return bot.reply_to(message, "✅ Specific filter 'all' deleted.")
        else:
            markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✅ Yes, Delete All", callback_data="hard_del_all_filters"),
                types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_del")
            )
            return bot.reply_to(message, "⚠️ <b>Warning!</b>\nKya aap sach mein saare filters database se saaf karna chahte hain?", reply_markup=markup)
    
    if db.delete_filter(target):
        bot.reply_to(message, f"🗑️ <b>Deleted:</b> <code>{html.escape(target)}</code>", parse_mode='HTML')
    else:
        bot.reply_to(message, "❌ <b>Filter nahi mila!</b> Check spelling via /filters.")

@bot.callback_query_handler(func=lambda call: call.data in ["hard_del_all_filters", "cancel_del"])
def handle_del_all_callback(call):
    if not db.is_admin(call.from_user.id): return
    if call.data == "hard_del_all_filters":
        count = db.delete_all_filters()
        bot.edit_message_text(f"🗑️ <b>All {count} filters deleted successfully!</b>", call.message.chat.id, call.message.message_id, parse_mode='HTML')
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)

### Bot by UNRATED CODER --- Support Our Channel @UNRATED_CODER ###
### --------> https://t.me/UNRATED_CODER <-------- 

@bot.message_handler(commands=['id'])
def send_id_info(message):
    # Target user: reply er user nai hoile command chalano user
    target_user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    chat = message.chat

    uid = target_user.id
    first_name = html.escape(target_user.first_name or "")
    mention = f'<a href="tg://user?id={uid}">{first_name}</a>'

    text = f"{mention}'s ID: <code>{uid}</code>"

    # Group info
    if chat.type in ['group', 'supergroup']:
        chat_name = html.escape(chat.title or "this group")
        text += f"\nGroup: <b>{chat_name}</b>\nGroup ID: <code>{chat.id}</code>"

    bot.reply_to(message, text, parse_mode="HTML")
