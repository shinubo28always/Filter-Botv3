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

# ================= HELP & ABOUT COMMANDS ==================
@bot.message_handler(commands=['help'])
def help_command(message):
    text = config.HELP_MSG
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🗑️ Close", callback_data="start_close", style='danger'))
    bot.reply_to(message, text, reply_markup=markup, parse_mode='HTML')

@bot.message_handler(commands=['about'])
def about_command(message):
    text = config.ABOUT_MSG
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("🗑️ Close", callback_data="start_close", style='danger'))
    bot.reply_to(message, text, reply_markup=markup, parse_mode='HTML')

# ================= START COMMAND LOGIC ==================
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
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✨ Join Updates ✨", url=config.LINK_ANIME_CHANNEL, style='success'))
        markup.row(
            types.InlineKeyboardButton("📖 Help", callback_data="start_help", style='primary'),
            types.InlineKeyboardButton("ℹ️ About", callback_data="start_about", style='primary')
        )
        markup.row(types.InlineKeyboardButton("➕ Add Bot to Group ➕", url=f"https://t.me/{bot.get_me().username}?startgroup=true", style='success'))

        try:
            bot.send_photo(chat_id, config.START_IMG, caption=pm_text, reply_markup=markup, parse_mode='HTML', message_effect_id=config.EFFECT_FIRE)
        except:
            bot.send_message(chat_id, pm_text, reply_markup=markup, parse_mode='HTML', message_effect_id=config.EFFECT_FIRE)
    else:
        group_text = config.GROUP_START_MSG.format(group_name=group_name)
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🤖 PM Me", url=f"https://t.me/{bot.get_me().username}?start=help", style='success')
        )
        try:
            bot.reply_to(message, group_text, reply_markup=markup, parse_mode='HTML')
        except:
            bot.send_message(chat_id, group_text, reply_markup=markup, parse_mode='HTML')


# ================= CALLBACK HANDLER FOR HELP/ABOUT/BACK/CLOSE ==================
@bot.callback_query_handler(func=lambda call: call.data in ["start_help", "start_about", "start_back", "start_close"])
def start_callback(call):
    uid = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    # 1. Close Button Logic
    if call.data == "start_close":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        return

    # 2. Help Button Logic
    if call.data == "start_help":
        text = config.HELP_MSG
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("⬅️ Back", callback_data="start_back", style='success'),
            types.InlineKeyboardButton("🗑️ Close", callback_data="start_close", style='danger')
        )
        # Edit Image Caption (if photo exists) or Text
        try:
            bot.edit_message_caption(text, chat_id, msg_id, reply_markup=markup, parse_mode='HTML')
        except:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode='HTML')

    # 3. About Button Logic
    elif call.data == "start_about":
        text = config.ABOUT_MSG
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("⬅️ Back", callback_data="start_back", style='success'),
            types.InlineKeyboardButton("🗑️ Close", callback_data="start_close", style='danger')
        )
        try:
            bot.edit_message_caption(text, chat_id, msg_id, reply_markup=markup, parse_mode='HTML')
        except:
            bot.edit_message_text(text, chat_id, msg_id, reply_markup=markup, parse_mode='HTML')

    # 4. Back Button Logic
    elif call.data == "start_back":
        first_name = html.escape(call.from_user.first_name)
        pm_text = config.PM_START_MSG.format(first_name=first_name)
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✨ Join Updates ✨", url=config.LINK_ANIME_CHANNEL, style='success'))
        markup.row(
            types.InlineKeyboardButton("📖 Help", callback_data="start_help", style='primary'),
            types.InlineKeyboardButton("ℹ️ About", callback_data="start_about", style='primary')
        )
        markup.row(types.InlineKeyboardButton("➕ Add Bot to Group ➕", url=f"https://t.me/{bot.get_me().username}?startgroup=true", style='success'))
        
        try:
            bot.edit_message_caption(pm_text, chat_id, msg_id, reply_markup=markup, parse_mode='HTML')
        except:
            bot.edit_message_text(pm_text, chat_id, msg_id, reply_markup=markup, parse_mode='HTML')

# ==========================================
# 👇 ADMIN & UTILITY COMMANDS
# ==========================================

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    s = time.time()
    msg = bot.reply_to(message, "⚡")
    bot.edit_message_text(f"📶 <b>Pong:</b> <code>{round((time.time()-s)*1000)}ms</code>", message.chat.id, msg.message_id, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not db.is_admin(message.from_user.id):
        return bot.reply_to(message, config.ROAST_GENERAL, parse_mode="HTML")
    u_count = len(db.get_all_users())
    f_count = len(db.get_all_filters_list())

    top_grp = db.get_top_groups(5)
    grp_txt = "\n".join([f"• <b>{g['title']}</b>: {g.get('activity', 0)}" for g in top_grp]) if top_grp else "No data yet."

    res = (
        f"📊 <b>Bot Statistics:</b>\n\n"
        f"👤 Users: <code>{u_count}</code>\n"
        f"📂 Filters: <code>{f_count}</code>\n\n"
        f"🏆 <b>Top 5 Active Groups:</b>\n{grp_txt}"
    )
    bot.reply_to(message, res, parse_mode='HTML')

@bot.message_handler(commands=['topsearch'])
def topsearch_cmd(message):
    uid = message.from_user.id
    is_admin = db.is_admin(uid)

    # Fetch Top 10
    top = db.get_top_searches(10)
    if not top:
        return bot.reply_to(message, "🔥 <b>No searches tracked yet.</b>", parse_mode='HTML')

    top_txt = "\n".join([f"{i+1}. <b>{t.get('title', t.get('keyword', 'Unknown')).upper()}</b> — <code>{t['count']}</code>" for i, t in enumerate(top)])
    res = f"🔥 <b>Top 10 Trending Anime:</b>\n\n{top_txt}"

    markup = types.InlineKeyboardMarkup()
    if is_admin:
        markup.row(
            types.InlineKeyboardButton("🔄 Refresh", callback_data="top_refresh", style='success'),
            types.InlineKeyboardButton("🗑️ Reset", callback_data="top_reset", style='danger')
        )
    markup.add(types.InlineKeyboardButton("🗑️ Close", callback_data="start_close", style='danger'))
    bot.reply_to(message, res, reply_markup=markup, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data in ["top_refresh", "top_reset"])
def topsearch_callback(call):
    uid = call.from_user.id
    if not db.is_admin(uid):
        return bot.answer_callback_query(call.id, "⚠️ Admin only!", show_alert=True)

    if call.data == "top_reset":
        db.clear_top_searches()
        bot.answer_callback_query(call.id, "✅ Top searches cleared!", show_alert=True)
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        return

    # Refresh Logic
    top = db.get_top_searches(10)
    if not top:
        bot.answer_callback_query(call.id, "📂 No data left.")
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        return

    top_txt = "\n".join([f"{i+1}. <b>{t.get('title', t.get('keyword', 'Unknown')).upper()}</b> — <code>{t['count']}</code>" for i, t in enumerate(top)])
    res = f"🔥 <b>Top 10 Trending Anime:</b>\n\n{top_txt}"

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🔄 Refresh", callback_data="top_refresh", style='success'),
        types.InlineKeyboardButton("🗑️ Reset", callback_data="top_reset", style='danger')
    )
    markup.add(types.InlineKeyboardButton("🗑️ Close", callback_data="start_close", style='danger'))

    try:
        bot.edit_message_text(res, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='HTML')
        bot.answer_callback_query(call.id, "✅ Refreshed!")
    except:
        bot.answer_callback_query(call.id, "Already Up-to-Date")

@bot.message_handler(commands=['filters'])
def list_filters(message):
    if not db.is_admin(message.from_user.id):
        return bot.reply_to(message, config.ROAST_GENERAL, parse_mode="HTML")
    fs = db.get_all_filters_list()
    if not fs: return bot.reply_to(message, "📂 <b>Database is empty!</b>")

    lines = [str(x['keyword']) for x in fs]
    full_text = "\n".join(lines)

    if len(full_text) <= 3800:
        safe_lines = [f"• <code>{html.escape(k)}</code>" for k in lines]
        txt = "📂 <b>Available Filters:</b>\n\n" + "\n".join(safe_lines)
        return bot.reply_to(message, txt, parse_mode="HTML")

    file = io.BytesIO(full_text.encode("utf-8"))
    file.name = "filters_list.txt"
    bot.send_document(message.chat.id, file, caption="📂 <b>Full Filter List</b>", parse_mode="HTML")

@bot.message_handler(commands=['del_filter'])
def delete_filter_cmd(message):
    if not db.is_admin(message.from_user.id):
        return bot.reply_to(message, config.ROAST_GENERAL, parse_mode="HTML")
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: return bot.reply_to(message, "⚠️ <b>Usage:</b> <code>/del_filter name</code>")
    target = parts[1].lower().strip()
    if target == "all":
        markup = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ Confirm All", callback_data="hard_del_all_filters", style='danger'),
            types.InlineKeyboardButton("❌ Cancel", callback_data="start_close", style='success')
        )
        return bot.reply_to(message, "⚠️ <b>Warning!</b>\nDelete all filters?", reply_markup=markup)
    if db.delete_filter(target):
        bot.reply_to(message, f"🗑️ <b>Deleted:</b> <code>{html.escape(target)}</code>", parse_mode='HTML')
    else:
        bot.reply_to(message, "❌ <b>Filter not found!</b>")

@bot.callback_query_handler(func=lambda call: call.data == "hard_del_all_filters")
def handle_del_all_callback(call):
    if not db.is_admin(call.from_user.id): return
    count = db.delete_all_filters()
    bot.edit_message_text(f"🗑️ <b>Total {count} filters deleted!</b>", call.message.chat.id, call.message.message_id, parse_mode='HTML')

@bot.message_handler(commands=['me'])
def user_profile_handler(message):
    uid = message.from_user.id
    first_name = html.escape(message.from_user.first_name)

    u_data = db.get_user_info(uid)
    rank = "Owner 👑" if str(uid) == str(config.OWNER_ID) else ("Admin 👮" if db.is_admin(uid) else "User 👤")

    joined_date = "Unknown"
    if u_data and 'joined_at' in u_data:
        joined_date = time.strftime("%Y-%m-%d", time.gmtime(u_data['joined_at']))

    text = (
        f"👤 <b>User Profile:</b>\n\n"
        f"🏷 <b>Name:</b> {first_name}\n"
        f"🆔 <b>ID:</b> <code>{uid}</code>\n"
        f"🎖 <b>Rank:</b> {rank}\n"
        f"📅 <b>Joined:</b> {joined_date}"
    )
    bot.reply_to(message, text, parse_mode="HTML")

@bot.message_handler(commands=['id'])
def send_id_info(message):
    if message.reply_to_message:
        # Replying to a message: Get IDs of the replied source
        rep = message.reply_to_message

        if rep.forward_from:
            # User forwarded message
            text = f"👤 <b>User ID:</b> <code>{rep.forward_from.id}</code>"
        elif rep.forward_from_chat:
            # Channel/Group forwarded message
            text = f"📢 <b>Chat ID:</b> <code>{rep.forward_from_chat.id}</code>"
        elif rep.from_user:
            # Direct message from user
            text = f"👤 <b>User ID:</b> <code>{rep.from_user.id}</code>"
            if rep.chat.type in ['group', 'supergroup', 'channel']:
                text += f"\n📢 <b>Chat ID:</b> <code>{rep.chat.id}</code>"
        else:
            text = f"📢 <b>Chat ID:</b> <code>{rep.chat.id}</code>"
    else:
        # Not replying: Show sender and current chat IDs
        uid = message.from_user.id
        text = f"👤 <b>Your ID:</b> <code>{uid}</code>"
        if message.chat.type != 'private':
            text += f"\n📢 <b>Chat ID:</b> <code>{message.chat.id}</code>"

    bot.reply_to(message, text, parse_mode="HTML")

### Bot by UNRATED CODER --- Support Our Channel @UNRATED_CODER ###
### --------> https://t.me/UNRATED_CODER <-------- ###
