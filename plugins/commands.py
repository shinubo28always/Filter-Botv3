import time
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
    
    # --- 1. HANDLE DEEP LINKING (REQUEST PARAMETER) ---
    if message.chat.type == "private" and len(message.text.split()) > 1:
        if message.text.split()[1] == "request":
            from plugins.request import initiate_request_flow
            initiate_request_flow(uid)
            return

    # --- 2. COMMON STICKER ANIMATION ---
    try:
        stk = bot.send_sticker(chat_id, config.STICKER_ID)
        time.sleep(1.2) # Sticker 1.2 sec tak dikhega
        bot.delete_message(chat_id, stk.message_id)
    except:
        pass

    # --- 3. PM (PRIVATE CHAT) START MSG ---
    if message.chat.type == "private":
        # Image with Caption and Buttons
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("✨ Join Updates ✨", url=config.LINK_ANIME_CHANNEL)
        )
        # Add Bot link generator
        bot_username = bot.get_me().username
        markup.add(
            types.InlineKeyboardButton("➕ Add Bot Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true")
        )
        
        pm_text = (
            "🎬 <b>Wᴇʟᴄᴏᴍᴇ ᴛᴏ Aɴɪᴍᴇ Fɪʟᴛᴇʀ Bᴏᴛ!</b>\n\n"
            "Hᴇʏ ᴛʜᴇʀᴇ! I’ᴍ ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ Aɴɪᴍᴇ Cʜᴀɴɴᴇʟ Fɪʟᴛᴇʀ Bᴏᴛ 💫\n"
            "• I ᴏɴʟʏ ᴘʀᴏᴠɪᴅᴇ ᴠᴇʀɪꜰɪᴇᴅ Aɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋs ꜰᴏʀ ʏᴏᴜ.\n"
            "• Iꜰ ᴀɴʏ ʟɪɴᴋ ᴅᴏᴇsɴ’ᴛ ᴡᴏʀᴋ, ᴊᴜsᴛ ʀᴇᴘᴏʀᴛ ɪɴ sᴜᴘᴘᴏʀᴛ.\n\n"
            "✨ <i>Just type Anime Name to search!</i>"
        )
        
        try:
            # Config se START_IMG uthayega (Default placeholder agar khali ho)
            img_url = getattr(config, 'START_IMG', 'https://telegra.ph/file/ed156093d6e5d95687747.jpg')
            bot.send_photo(
                chat_id, 
                img_url, 
                caption=pm_text, 
                reply_markup=markup, 
                parse_mode='HTML',
                message_effect_id=config.EFFECT_FIRE
            )
        except:
            bot.send_message(chat_id, pm_text, reply_markup=markup, message_effect_id=config.EFFECT_FIRE)

    # --- 4. GROUP START MSG ---
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🤖 PM Mᴇ", url=f"https://t.me/{bot.get_me().username}?start=help"))
        
        group_text = (
            "👋 <b>Hᴇʏ! I ᴀᴍ Aʟɪᴠᴇ.</b>\n\n"
            "Jᴜsᴛ ᴛʏᴘᴇ ᴛʜᴇ Aɴɪᴍᴇ Nᴀᴍᴇ ᴛᴏ ɢᴇᴛ ʟɪɴᴋs.\n"
            "Mᴀᴋᴇ sᴜʀᴇ I ᴀᴍ Aᴅᴍɪɴ ʜᴇʀᴇ!"
        )
        bot.send_message(chat_id, group_text, reply_markup=markup, message_effect_id=config.EFFECT_FIRE)

# --- 5. OTHER COMMANDS (PING, STATS, FILTERS, DEL_FILTER) ---

@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    start = time.time()
    msg = bot.reply_to(message, "⚡ <b>Calculating...</b>")
    ms = round((time.time() - start) * 1000)
    bot.edit_message_text(f"📶 <b>Pong:</b> <code>{ms}ms</code>", message.chat.id, msg.message_id)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not db.is_admin(message.from_user.id): return
    u_count = len(db.get_all_users())
    f_count = len(db.get_all_filters_list())
    bot.reply_to(message, f"📊 <b>Bot Statistics:</b>\n\n👤 Users: <code>{u_count}</code>\n📂 Filters: <code>{f_count}</code>")

@bot.message_handler(commands=['filters'])
def list_filters(message):
    if not db.is_admin(message.from_user.id): return
    fs = db.get_all_filters_list()
    if not fs: return bot.reply_to(message, "📂 <b>Database Khali Hai!</b>")
    
    txt = "📂 <b>Available Filters:</b>\n\n" + "\n".join([f"• <code>{x['keyword']}</code>" for x in fs])
    if len(txt) > 4000:
        with open("filters.txt", "w") as f: f.write(txt)
        with open("filters.txt", "rb") as f: bot.send_document(message.chat.id, f)
    else:
        bot.reply_to(message, txt)

@bot.message_handler(commands=['del_filter'])
def delete_filter_cmd(message):
    if not db.is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: /del_filter name/all")
    
    target = args[1].lower()
    if target == "all":
        # Check if specific filter named 'all' exists
        if db.get_filter("all"):
            db.delete_filter("all")
            bot.reply_to(message, "✅ Filter 'all' delete ho gaya.")
        else:
            markup = types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("✅ Confirm All Delete", callback_data="conf_del_all"),
                types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_del")
            )
            bot.reply_to(message, "⚠️ <b>Warning:</b> Saare filters delete karne hain?", reply_markup=markup)
    else:
        if db.delete_filter(target): bot.reply_to(message, f"🗑️ Filter <code>{target}</code> deleted.")
        else: bot.reply_to(message, "❌ Filter nahi mila.")

@bot.callback_query_handler(func=lambda call: call.data in ["conf_del_all", "cancel_del"])
def handle_del_callback(call):
    if not db.is_admin(call.from_user.id): return
    if call.data == "conf_del_all":
        count = db.delete_all_filters()
        bot.edit_message_text(f"🗑️ <b>Total {count} filters clear kar diye gaye!</b>", call.message.chat.id, call.message.message_id)
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
