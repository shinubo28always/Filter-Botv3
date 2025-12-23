import time
import os
from bot_instance import bot
import config
import database as db
from telebot import types

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def start_handler(message):
    uid = message.from_user.id
    chat_id = message.chat.id
    db.add_user(uid)
    
    if message.chat.type == "private" and len(message.text.split()) > 1:
        if message.text.split()[1] == "request":
            from plugins.request import initiate_request_flow
            initiate_request_flow(uid)
            return

    try:
        stk = bot.send_sticker(chat_id, config.STICKER_ID)
        time.sleep(1.2)
        bot.delete_message(chat_id, stk.message_id)
    except: pass

    if message.chat.type == "private":
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✨ Join Updates ✨", url=config.LINK_ANIME_CHANNEL))
        bot_username = bot.get_me().username
        markup.add(types.InlineKeyboardButton("➕ Add Bot Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true"))
        
        pm_text = (
            "🎬 <b>Wᴇʟᴄᴏᴍᴇ ᴛᴏ Aɴɪᴍᴇ Fɪʟᴛᴇʀ Bᴏᴛ!</b>\n\n"
            "Hᴇʏ ᴛʜᴇʀᴇ! I’ᴍ ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ Aɴɪᴍᴇ Cʜᴀɴɴᴇʟ Fɪʟᴛᴇʀ Bᴏᴛ 💫\n"
            "• I ᴏɴʟʏ ᴘʀᴏᴠɪᴅᴇ ᴠᴇʀɪꜰɪᴇᴅ Aɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋs ꜰᴏʀ ʏᴏᴜ.\n"
            "• Iꜰ ᴀɴʏ ʟɪɴᴋ ᴅᴏᴇsɴ’ᴛ ᴡᴏʀᴋ, ᴊᴜsᴛ ʀᴇᴘᴏʀᴛ ɪɴ sᴜᴘᴘᴏʀᴛ.\n\n"
            "✨ <i>Just type Anime Name to search!</i>"
        )
        try:
            img_url = getattr(config, 'START_IMG', 'https://telegra.ph/file/ed156093d6e5d95687747.jpg')
            bot.send_photo(chat_id, img_url, caption=pm_text, reply_markup=markup, parse_mode='HTML')
        except:
            bot.send_message(chat_id, pm_text, reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🤖 PM Mᴇ", url=f"https://t.me/{bot.get_me().username}?start=help"))
        bot.send_message(chat_id, "👋 <b>Hᴇʏ! I ᴀᴍ Aʟɪᴠᴇ.</b>\n\nJᴜsᴛ ᴛʏᴘᴇ ᴛʜᴇ Aɴɪᴍᴇ Nᴀᴍᴇ ᴛᴏ ɢᴇᴛ ʟɪɴᴋs.", reply_markup=markup)

# --- PING & STATS ---
@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    start = time.time()
    msg = bot.reply_to(message, "⚡")
    ms = round((time.time() - start) * 1000)
    bot.edit_message_text(f"📶 <b>Pong:</b> <code>{ms}ms</code>", message.chat.id, msg.message_id)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not db.is_admin(message.from_user.id): return
    u = len(db.get_all_users())
    f = len(db.get_all_filters_list())
    bot.reply_to(message, f"📊 <b>Stats:</b>\nUsers: <code>{u}</code>\nFilters: <code>{f}</code>")

# --- FILTER LISTING ---
@bot.message_handler(commands=['filters'])
def list_filters(message):
    if not db.is_admin(message.from_user.id): return
    fs = db.get_all_filters_list()
    if not fs: return bot.reply_to(message, "📂 Database Khali Hai!")
    
    txt = "📂 <b>Available Filters:</b>\n\n" + "\n".join([f"• <code>{x['keyword']}</code>" for x in fs])
    if len(txt) > 4000:
        with open("filters.txt", "w") as f: f.write(txt)
        with open("filters.txt", "rb") as f: bot.send_document(message.chat.id, f)
        os.remove("filters.txt")
    else:
        bot.reply_to(message, txt)

# --- DELETE FILTER LOGIC ---
@bot.message_handler(commands=['del_filter'])
def delete_filter_cmd(message):
    if not db.is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: /del_filter name/all")
    
    target = args[1].lower()
    if target == "all":
        # Check if a filter specifically named 'all' exists
        if db.get_filter("all"):
            db.delete_filter("all")
            return bot.reply_to(message, "✅ Filter 'all' delete ho gaya.")
        else:
            # Show Confirmation Buttons
            markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✅ Confirm Delete All", callback_data="confirm_delete_all_filters"),
                types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_filter_del")
            )
            return bot.reply_to(message, "⚠️ <b>Warning:</b> Kya aap database ke saare filters delete karna chahte hain?", reply_markup=markup)
    else:
        if db.delete_filter(target): bot.reply_to(message, f"🗑️ Filter <code>{target}</code> deleted.")
        else: bot.reply_to(message, "❌ Filter nahi mila.")

# --- DELETE ALL FILTERS CALLBACK ---
@bot.callback_query_handler(func=lambda call: call.data in ["confirm_delete_all_filters", "cancel_filter_del"])
def handle_del_all_callback(call):
    # Security: Sirf admins click kar sakte hain
    if not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "Baka! Only Admins.", show_alert=True)

    if call.data == "confirm_delete_all_filters":
        count = db.delete_all_filters()
        bot.answer_callback_query(call.id, "Cleaning Database...", show_alert=False)
        bot.edit_message_text(f"🗑️ <b>All {count} filters have been deleted successfully!</b>", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "Action Cancelled.", show_alert=False)
        bot.delete_message(call.message.chat.id, call.message.message_id)
