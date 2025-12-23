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
    
    # --- 1. HANDLE DEEP LINKING (GC Redirect Case) ---
    if message.chat.type == "private" and len(message.text.split()) > 1:
        param = message.text.split()[1]
        if param == "request":
            from plugins.request import initiate_request_flow
            initiate_request_flow(uid)
            return

    # --- 2. COMMON STICKER ANIMATION ---
    try:
        stk = bot.send_sticker(chat_id, config.STICKER_ID)
        time.sleep(1.2)
        bot.delete_message(chat_id, stk.message_id)
    except:
        pass

    # --- 3. PM (PRIVATE CHAT) START MSG ---
    if message.chat.type == "private":
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("✨ Join Updates ✨", url=config.LINK_ANIME_CHANNEL))
        bot_username = bot.get_me().username
        markup.add(types.InlineKeyboardButton("➕ Add Bot Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true"))
        
        pm_text = (
            "🎬 <b>Wᴇʟᴄᴏᴍᴇ ᴛᴏ Aɴɪᴍᴇ Fɪʟᴛᴇʀ Bᴏᴛ!</b>\n\n"
            "Hᴇʏ ᴛʜᴇʀᴇ! I’ᴍ ʏᴏᴜʀ ᴘᴇʀsᴏɴᴀʟ Aɴɪᴍᴇ Cʜᴀɴɴᴇʟ Fɪʟᴛᴇʀ Bᴏᴛ 💫\n"
            "• I ᴏɴʟʏ ᴘʀᴏᴠɪᴅᴇ ᴠᴇʀɪꜰɪᴇᴅ Aɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ ʟɪɴᴋs ꜰᴏʀ ʏᴏᴜ.\n\n"
            "✨ <i>Just type Anime Name to search!</i>"
        )
        
        try:
            img_url = getattr(config, 'START_IMG', 'https://telegra.ph/file/ed156093d6e5d95687747.jpg')
            bot.send_photo(chat_id, img_url, caption=pm_text, reply_markup=markup, message_effect_id=config.EFFECT_FIRE)
        except:
            bot.send_message(chat_id, pm_text, reply_markup=markup, message_effect_id=config.EFFECT_FIRE)

    # --- 4. GROUP START MSG (REPLY MODE - NO EFFECTS) ---
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🤖 PM Mᴇ", url=f"https://t.me/{bot.get_me().username}?start=help"))
        
        group_text = (
            "👋 <b>Hᴇʏ! I ᴀᴍ Aʟɪᴠᴇ.</b>\n\n"
            "Jᴜsᴛ ᴛʏᴘᴇ ᴛʜᴇ Aɴɪᴍᴇ Nᴀᴍᴇ ᴛᴏ ɢᴇᴛ ʟɪɴᴋs.\n"
            "Mᴀᴋᴇ sᴜʀᴇ I ᴀᴍ Aᴅᴍɪɴ ʜᴇʀᴇ!"
        )
        # Reply specifically to the user who used /start
        bot.reply_to(message, group_text, reply_markup=markup)

# --- STATS, FILTERS, DEL_FILTER handlers remain the same but use reply_to ---
@bot.message_handler(commands=['ping'])
def ping_cmd(message):
    start = time.time()
    msg = bot.reply_to(message, "⚡ <b>Calculating...</b>")
    ms = round((time.time() - start) * 1000)
    bot.edit_message_text(f"📶 <b>Pong:</b> <code>{ms}ms</code>", message.chat.id, msg.message_id)

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not db.is_admin(message.from_user.id): return
    u, f = len(db.get_all_users()), len(db.get_all_filters_list())
    bot.reply_to(message, f"📊 <b>Bot Statistics:</b>\n\n👤 Users: <code>{u}</code>\n📂 Filters: <code>{f}</code>")

@bot.message_handler(commands=['filters'])
def list_filters(message):
    if not db.is_admin(message.from_user.id): return
    fs = db.get_all_filters_list()
    if not fs: return bot.reply_to(message, "📂 Database Khali Hai!")
    txt = "📂 <b>Available Filters:</b>\n\n" + "\n".join([f"• <code>{x['keyword']}</code>" for x in fs])
    bot.reply_to(message, txt[:4000])

@bot.message_handler(commands=['del_filter'])
def delete_filter_cmd(message):
    if not db.is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: /del_filter name/all")
    target = args[1].lower()
    if target == "all":
        markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ Confirm All", callback_data="conf_del_all"))
        bot.reply_to(message, "⚠️ Saare filters delete karne hain?", reply_markup=markup)
    else:
        if db.delete_filter(target): bot.reply_to(message, f"🗑️ Filter <code>{target}</code> deleted.")
        else: bot.reply_to(message, "❌ Not found.")
