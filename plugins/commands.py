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
    db.add_user(uid)
    
    # --- 1. DEEP LINKING (REQUEST REDIRECT) ---
    if message.chat.type == "private" and len(message.text.split()) > 1:
        if message.text.split()[1] == "request":
            from plugins.request import initiate_request_flow
            initiate_request_flow(uid)
            return

    # --- 2. STICKER ANIMATION ---
    try:
        stk = bot.send_sticker(chat_id, config.STICKER_ID)
        time.sleep(1.2)
        bot.delete_message(chat_id, stk.message_id)
    except: pass

    # --- 3. START MESSAGE LOGIC ---
    if message.chat.type == "private":
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✨ Join Updates ✨", url=config.LINK_ANIME_CHANNEL))
        markup.add(types.InlineKeyboardButton("➕ Add Bot to Group ➕", url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
        
        pm_text = (
            "🎬 <b>Wᴇʟᴄᴏᴍᴇ ᴛᴏ Aɴɪᴍᴇ Fɪʟᴛᴇʀ Bᴏᴛ!</b>\n\n"
            "Hᴇʏ ᴛʜᴇʀᴇ! I’ᴍ ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ Aɴɪᴍᴇ Cʜᴀɴɴᴇʟ Fɪʟᴛᴇʀ Bᴏᴛ 💫\n"
            "• I ᴏɴʟʏ ᴘʀᴏᴠɪᴅᴇ ᴠᴇʀɪꜰɪᴇᴅ Aɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋs.\n"
            "• Jᴜsᴛ ᴛʏᴘᴇ ᴀɴɪᴍᴇ ɴᴀᴍᴇ ᴛᴏ sᴇᴀʀᴄʜ!"
        )
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
            bot.send_message(chat_id, pm_text, reply_markup=markup, message_effect_id=config.EFFECT_FIRE)
    else:
        # Group Start Msg
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🤖 PM Mᴇ", url=f"https://t.me/{bot.get_me().username}?start=help"))
        bot.send_message(chat_id, "👋 <b>Hᴇʏ! I ᴀᴍ Aʟɪᴠᴇ.</b>\nJᴜsᴛ ᴛʏᴘᴇ Anime Nᴀᴍᴇ ᴛᴏ sᴇᴀʀᴄʜ.", reply_markup=markup, parse_mode="HTML")

# --- 4. ADMIN COMMANDS (FILTERS, STATS, PING) ---

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    start = time.time()
    msg = bot.reply_to(message, "⚡")
    ms = round((time.time() - start) * 1000)
    bot.edit_message_text(f"📶 <b>Pong:</b> <code>{ms}ms</code>", message.chat.id, msg.message_id)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not db.is_admin(message.from_user.id): return
    bot.reply_to(message, f"📊 <b>Stats:</b>\nUsers: {len(db.get_all_users())}\nFilters: {len(db.get_all_filters_list())}")

@bot.message_handler(commands=['filters'])
def list_filters(message):
    if not db.is_admin(message.from_user.id): return
    fs = db.get_all_filters_list()
    if not fs: return bot.reply_to(message, "📂 Database Khali Hai!")
    txt = "📂 <b>Available Filters:</b>\n\n" + "\n".join([f"• <code>{x['keyword']}</code>" for x in fs])
    if len(txt) > 4000:
        with open("filters.txt", "w") as f: f.write(txt)
        with open("filters.txt", "rb") as f: bot.send_document(message.chat.id, f); os.remove("filters.txt")
    else:
        bot.reply_to(message, txt)

# --- 5. DELETE FILTER (HARD SPACE FIX) ---
@bot.message_handler(commands=['del_filter'])
def delete_filter_cmd(message):
    if not db.is_admin(message.from_user.id): return
    
    # capture full input after command (e.g. witch watch)
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2: return bot.reply_to(message, "⚠️ Usage: /del_filter name or all")
    
    target = parts[1].lower().strip()
    
    if target == "all":
        # Check if filter named 'all' exists
        if db.get_filter("all"):
            db.delete_filter("all")
            return bot.reply_to(message, "✅ Filter 'all' deleted.")
        else:
            markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✅ Confirm All Delete", callback_data="hard_del_all_filters"),
                types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_del")
            )
            return bot.reply_to(message, "⚠️ <b>Warning:</b> Database saaf karna hai?", reply_markup=markup)
    else:
        if db.delete_filter(target):
            bot.reply_to(message, f"🗑️ Deleted: <code>{target}</code>")
        else:
            bot.reply_to(message, "❌ Filter nahi mila.")

@bot.callback_query_handler(func=lambda call: call.data in ["hard_del_all_filters", "cancel_del"])
def handle_del_all(call):
    if not db.is_admin(call.from_user.id): return
    if call.data == "hard_del_all_filters":
        count = db.delete_all_filters()
        bot.edit_message_text(f"🗑️ <b>All {count} filters deleted!</b>", call.message.chat.id, call.message.message_id)
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
