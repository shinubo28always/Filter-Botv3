### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

import time
import config
import database as db
from bot_instance import bot
from telebot import types
from thefuzz import process, fuzz

# ---------------- SETTINGS ----------------
ITEMS_PER_PAGE = 5   # 5 Rows (1 anime per row)
FUZZY_THRESHOLD = 80 # Strict search

# ---------------- MESSAGE HANDLER ----------------
@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    if message.text.startswith("/"):
        return

    uid = message.from_user.id
    db.add_user(uid)
    query = message.text.lower().strip()

    # ---------------- 1. FSUB CHECK (ONLY PM) ----------------
    if message.chat.type == "private":
        all_fsubs = db.get_all_fsub()
        missing_normals = []
        request_fsubs = [f for f in all_fsubs if f.get("mode") == "request"]

        for f in all_fsubs:
            if f.get("mode") == "request": continue
            try:
                st = bot.get_chat_member(int(f['_id']), uid).status
                if st not in ['member', 'administrator', 'creator']:
                    missing_normals.append(f)
            except:
                missing_normals.append(f)

        if missing_normals:
            return send_fsub_message(message, missing_normals, request_fsubs)

    # ---------------- 2. ALPHABET INDEX SYSTEM ----------------
    if len(query) == 1 and query.isalpha():
        send_index_page(message.chat.id, query, 1, message.message_id, uid, is_new=True)
        return

    # ---------------- 3. SEARCH ENGINE ----------------
    choices = db.get_all_keywords()
    if not choices:
        return

    matches = process.extract(query, choices, limit=15, scorer=fuzz.token_sort_ratio)
    best_matches = [m for m in matches if m[1] >= FUZZY_THRESHOLD]
    
    if not best_matches:
        if message.chat.type == "private":
            bot.reply_to(message, "❌ <b>No results found!</b>\nCheck spelling or send a single letter (e.g. 'A') to browse.")
        return

    # Exact match (Score 95+)
    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
        return

    # Suggestions (Filtering duplicates)
    markup = types.InlineKeyboardMarkup()
    seen = set()
    for b in best_matches:
        row = db.get_filter(b[0])
        if row and row['title'] not in seen:
            cb = f"fuz|{b[0][:20]}|{message.message_id}|{uid}"
            markup.add(types.InlineKeyboardButton(f"🎬 {row['title']}", callback_data=cb))
            seen.add(row['title'])
            if len(seen) >= 5: break 

    if seen:
        bot.reply_to(message, "🧐 <b>Did you mean:</b>", reply_markup=markup)


# ---------------- INDEX PAGE GENERATOR ----------------
def send_index_page(chat_id, letter, page, original_mid, uid, is_new=False, edit_mid=None):
    all_kws = db.get_all_keywords()
    filtered_kws = [kw for kw in all_kws if kw.startswith(letter)]
    
    unique_results = []
    seen_titles = set()
    for kw in filtered_kws:
        data = db.get_filter(kw)
        if data and data['title'] not in seen_titles:
            unique_results.append({"kw": kw, "title": data['title']})
            seen_titles.add(data['title'])

    if not unique_results:
        if is_new: bot.send_message(chat_id, f"📂 No anime found starting with <b>'{letter.upper()}'</b>")
        return

    total_pages = (len(unique_results) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = unique_results[start:end]

    markup = types.InlineKeyboardMarkup()
    for item in page_items:
        markup.add(types.InlineKeyboardButton(f"🎬 {item['title']}", callback_data=f"fuz|{item['kw'][:20]}|{original_mid}|{uid}"))

    # Navigation logic
    nav_row = []
    if page > 1:
        nav_row.append(types.InlineKeyboardButton("⬅️ Back", callback_data=f"ind|{letter}|{page-1}|{uid}|{original_mid}"))
    
    nav_row.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="none"))
    
    if page < total_pages:
        nav_row.append(types.InlineKeyboardButton("Next ➡️", callback_data=f"ind|{letter}|{page+1}|{uid}|{original_mid}"))
    
    markup.row(*nav_row)

    text = f"📂 <b>Anime Index: '{letter.upper()}'</b>\nTotal Results: <code>{len(unique_results)}</code>"
    
    try:
        if is_new:
            bot.send_message(chat_id, text, reply_markup=markup, reply_to_message_id=original_mid)
        else:
            bot.edit_message_text(text, chat_id, edit_mid, reply_markup=markup)
    except Exception as e:
        print(f"Index UI Error: {e}")


# ---------------- CALLBACK HANDLER ----------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    clicker_id = call.from_user.id
    data = call.data.split("|")

    # 1. INDEX NAVIGATION (FIXED)
    if data[0] == "ind":
        letter, page, ouid, original_mid = data[1], int(data[2]), int(data[3]), int(data[4])
        
        # User Lock
        if clicker_id != ouid and not db.is_admin(clicker_id):
            return bot.answer_callback_query(call.id, "⚠️ Search yourself @UNRATED_CODER", show_alert=True)
        
        # Edit the current message with the new page
        send_index_page(call.message.chat.id, letter, page, original_mid, ouid, is_new=False, edit_mid=call.message.message_id)
        bot.answer_callback_query(call.id) # Loading spinner stop
        return

    # 2. RESULT HANDLER
    if data[0] == "fuz":
        key, mid, ouid = data[1], int(data[2]), int(data[3])
        if clicker_id != ouid and not db.is_admin(clicker_id):
            return bot.answer_callback_query(call.id, "⚠️ Not your request @UNRATED_CODER", show_alert=True)

        # FSub Re-check
        if call.message.chat.type == "private":
            missing = []
            for f in db.get_all_fsub():
                if f.get("mode") == "request": continue
                try:
                    st = bot.get_chat_member(int(f['_id']), clicker_id).status
                    if st not in ['member', 'administrator', 'creator']: missing.append(f)
                except: missing.append(f)
            if missing:
                bot.answer_callback_query(call.id, "❌ Join channels first!", show_alert=True)
                return send_fsub_message(call.message, missing, [])

        filter_data = db.get_filter(key) or db.get_filter(process.extractOne(key, db.get_all_keywords())[0])
        if filter_data:
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            send_final_result(call.message, filter_data, mid)


# ---------------- UTILS ----------------

def send_fsub_message(message, missing_normals, request_fsubs):
    markup = types.InlineKeyboardMarkup()
    expiry = int(time.time()) + 120
    for f in missing_normals:
        try:
            invite = bot.create_chat_invite_link(int(f['_id']), expire_date=expiry, creates_join_request=False)
            markup.add(types.InlineKeyboardButton(f"✨ Join Channel ✨", url=invite.invite_link))
        except: pass
    for r in request_fsubs:
        try:
            invite = bot.create_chat_invite_link(int(r['_id']), expire_date=expiry, creates_join_request=True)
            markup.add(types.InlineKeyboardButton(f"✨ Request to Join ✨", url=invite.invite_link))
        except: pass
    markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))
    bot.reply_to(message, "⚠️ <b>Access Restricted!</b>\nJoin our official channels to view results.", reply_markup=markup)

def send_final_result(message, data, r_mid):
    try:
        invite = bot.create_chat_invite_link(int(data['source_cid']), member_limit=0)
        link = invite.invite_link
    except: link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🎬 Watch / Download", url=link))
    try:
        bot.copy_message(message.chat.id, int(config.DB_CHANNEL_ID), int(data['db_mid']), reply_markup=markup, reply_to_message_id=r_mid)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>Error!</b>\n<code>{str(e)}</code>", reply_to_message_id=r_mid, parse_mode="HTML")

### Bot by UNRATED CODER --- Support Our Channel @UNRATED_CODER ###
### --------> https://t.me/UNRATED_CODER <-------- ###
