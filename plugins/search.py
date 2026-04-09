### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

import time, threading, config, database as db, re
from bot_instance import bot
from telebot import types, apihelper
from thefuzz import process, fuzz

ITEMS_PER_PAGE = 5   
FUZZY_THRESHOLD = 80 

# Simple in-memory rate limiting: {uid: last_search_time}
RATE_LIMITS = {}
COOLDOWN = 3 # 3 seconds cooldown between searches

def delete_msg_timer(chat_id, message_ids, delay):
    def delayed_delete():
        time.sleep(delay)
        for m_id in message_ids:
            try: bot.delete_message(chat_id, m_id)
            except: pass
    threading.Thread(target=delayed_delete).start()

@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    if message.text.startswith("/"): return
    uid = message.from_user.id

    # 0. BAN CHECK
    if db.is_banned(uid):
        return # Silently ignore banned users

    # 0. MAINTENANCE CHECK
    if db.get_maintenance() and not db.is_admin(uid):
        return bot.reply_to(message, "🛠 <b>Bot is under maintenance. Please try again later!</b>")

    # 0. RATE LIMIT CHECK
    now = time.time()
    if uid in RATE_LIMITS and (now - RATE_LIMITS[uid]) < COOLDOWN:
        return # Ignore spam silently to avoid errors in message handler
    RATE_LIMITS[uid] = now

    db.add_user(uid)
    if message.chat.type in ['group', 'supergroup']: db.track_group_activity(message.chat.id)
    query = message.text.lower().strip()

    # Track search ONLY if it's PM or if it looks like a real query (length check + not noise)
    # We delay tracking until we see if it has ANY matching potential to avoid group noise
    is_private = message.chat.type == "private"
    if message.chat.type == "private":
        all_fsubs = db.get_all_fsub()
        missing = []
        for f in all_fsubs:
            try:
                st = bot.get_chat_member(int(f['_id']), uid).status
                if st in ['member', 'administrator', 'creator', 'restricted']: continue

                if f.get("mode") == "request" and db.is_request_pending(uid, f['_id']):
                    continue

                missing.append(f)
            except:
                missing.append(f)

        if missing:
            return send_fsub_message(message, missing)

    # 2. ALPHABET INDEX (NOW FIXED)
    if len(query) == 1 and query.isalpha():
        wait_msg = bot.reply_to(message, f"🔍 <b>Searching for '{query.upper()}'...</b>")
        send_index_page(message.chat.id, query, 1, message.message_id, uid, edit_mid=wait_msg.message_id)
        # We don't delete message here because send_index_page handles the result display,
        # but the wait_msg/index_page will be deleted by delete_msg_timer in send_index_page
        return

    # 3. WORD-BOUNDARY KEYWORD MATCH (High Priority)
    all_kws = db.get_all_keywords()
    # Sort by length descending to match longest keyword first (e.g. "naruto shippuden" over "naruto")
    sorted_kws = sorted(all_kws, key=len, reverse=True)

    found_kw = None
    for kw in sorted_kws:
        if len(kw) < 2: continue # Ignore very short single letters

        # Use regex to match only as a distinct word/phrase (prevents matching "naruto" inside "abcnarutoxyz")
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, query):
            found_kw = kw
            break

    if found_kw:
        data = db.get_filter(found_kw)
        if data:
            db.track_anime_hit(data['title'])
            return send_final_result(message, data, message.message_id)

    # 4. FUZZY SEARCH
    matches = process.extract(query, all_kws, limit=10, scorer=fuzz.token_sort_ratio)
    best_matches = [m for m in matches if m[1] >= FUZZY_THRESHOLD]

    if not best_matches:
        if is_private:
            no_res = bot.reply_to(message, "❌ <b>No results found!</b>")
            delete_msg_timer(message.chat.id, [no_res.message_id, message.message_id], 300)
        return

    # If we reached here, we have matches.
    # But we ONLY track if it's high confidence or from a selection

    if best_matches[0][1] >= 90:
        data = db.get_filter(best_matches[0][0])
        if data:
            db.track_anime_hit(data['title']) # Track by title
            send_final_result(message, data, message.message_id)
    else:
        # Show selection menu for fuzzy matches
        markup = types.InlineKeyboardMarkup()
        seen_titles = set()
        for b in best_matches:
            row = db.get_filter(b[0])
            if row and row['title'] not in seen_titles:
                cb = f"res|{row['db_mid']}|{uid}|{message.message_id}"
                markup.add(types.InlineKeyboardButton(f"🎬 {row['title']}", callback_data=cb))
                seen_titles.add(row['title'])
                if len(seen_titles) >= 5: break 
        if seen_titles:
            s_msg = bot.reply_to(message, "🧐 <b>Did you mean:</b>", reply_markup=markup)
            delete_msg_timer(message.chat.id, [s_msg.message_id, message.message_id], 300)

def send_index_page(chat_id, letter, page, original_mid, uid, edit_mid=None):
    # Fetch from fixed database logic
    results = db.get_index_results(letter)
    
    unique_items = []
    seen_titles = set()
    for res in results:
        if res['title'] not in seen_titles:
            unique_items.append(res)
            seen_titles.add(res['title'])

    if not unique_items:
        bot.edit_message_text(f"📂 No results starting with <b>'{letter.upper()}'</b>", chat_id, edit_mid)
        return

    total_pages = (len(unique_items) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = (page - 1) * ITEMS_PER_PAGE
    page_items = unique_items[start:start + ITEMS_PER_PAGE]

    markup = types.InlineKeyboardMarkup()
    for item in page_items:
        # Direct Callback to avoid extra DB hits
        cb = f"res|{item['db_mid']}|{uid}|{original_mid}"
        markup.add(types.InlineKeyboardButton(f"🎬 {item['title']}", callback_data=cb))

    nav = []
    if page > 1: nav.append(types.InlineKeyboardButton("⬅️ Back", callback_data=f"ind|{letter}|{page-1}|{uid}|{original_mid}"))
    nav.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="none"))
    if page < total_pages: nav.append(types.InlineKeyboardButton("Next ➡️", callback_data=f"ind|{letter}|{page+1}|{uid}|{original_mid}"))
    markup.row(*nav)

    text = f"📂 <b>Anime Index: '{letter.upper()}'</b>\nTotal Results: <code>{len(unique_items)}</code>"
    try:
        bot.edit_message_text(text, chat_id, edit_mid, reply_markup=markup)
        # Auto-delete Index page and user message after 5 mins
        delete_msg_timer(chat_id, [edit_mid, original_mid], 300)
    except: pass

@bot.callback_query_handler(func=lambda call: call.data.startswith(('ind', 'res', 'check_fsub')))
def handle_callbacks(call):
    data = call.data.split("|")
    
    # 1. Validation Logic
    if data[0] == "ind":
        searcher_id = int(data[3]) 
    elif data[0] == "res":
        searcher_id = int(data[2])
    elif data[0] == "check_fsub":
        # Anyone can click Try Again, it will re-check their status
        bot.answer_callback_query(call.id, "Checking...")
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        bot.send_message(call.message.chat.id, "<b>Re-check complete. Please search for your anime again!</b>", parse_mode="HTML")
        return
    else:
        return # Agar koi aur button ho toh ignore karein

    # 2. User Check
    if searcher_id and call.from_user.id != searcher_id and not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(call.id, "⚠️ Not your request!", show_alert=True)

    bot.answer_callback_query(call.id)

    # 3. Index Page Handling
    if data[0] == "ind":
        send_index_page(
            call.message.chat.id, 
            data[1],             # letter
            int(data[2]),        # page
            int(data[4]),        # original_mid
            int(data[3]),        # uid
            edit_mid=call.message.message_id
        )
    
    # 4. Result Handling
    elif data[0] == "res":
        filter_data = db.get_filter_by_mid(int(data[1]))
        if filter_data:
            db.track_anime_hit(filter_data['title']) # Track by title
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            send_final_result(call.message, filter_data, int(data[3]))


def send_final_result(message, data, r_mid):
    is_slot = data.get('type') == 'slot'
    settings = db.get_bot_settings()
    del_time = settings.get('auto_delete', 300)
    try:
        markup = types.InlineKeyboardMarkup()
        if is_slot:
            # Custom buttons support
            for btn in data.get('custom_buttons', []): markup.add(types.InlineKeyboardButton(btn['name'], url=btn['url']))
            res_msg = bot.copy_message(message.chat.id, int(config.DB_CHANNEL_ID), int(data['db_mid']), reply_markup=markup if data.get('custom_buttons') else None, reply_to_message_id=r_mid)
        else:
            # Manual Filter: Dynamic Expiry and Button Text
            try:
                chat_info = bot.get_chat(int(data['source_cid']))
                if chat_info.username: # Public Channel
                    expire_sec = settings.get('public_expiry', 300)
                else: # Private Channel
                    expire_sec = settings.get('private_expiry', 120)
            except:
                expire_sec = 300 # Fallback

            expire_time = int(time.time() + expire_sec)
            invite = bot.create_chat_invite_link(int(data['source_cid']), expire_date=expire_time, member_limit=1)

            btn_text = settings.get('button_text', "Watch & Download")
            markup.add(types.InlineKeyboardButton(f"🎬 {btn_text}", url=invite.invite_link))
            res_msg = bot.copy_message(message.chat.id, int(config.DB_CHANNEL_ID), int(data['db_mid']), reply_markup=markup, reply_to_message_id=r_mid)

        delete_msg_timer(message.chat.id, [res_msg.message_id, r_mid], del_time)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>Error!</b>\n<code>{str(e)}</code>", reply_to_message_id=r_mid)

def send_fsub_message(message, missing):
    markup = types.InlineKeyboardMarkup()
    for f in missing:
        cid = int(f['_id'])
        if f.get('mode') == 'request':
            invite = bot.create_chat_invite_link(cid, creates_join_request=True)
            markup.add(types.InlineKeyboardButton("✨ Request to Join ✨", url=invite.invite_link))
        else:
            invite = bot.create_chat_invite_link(cid)
            markup.add(types.InlineKeyboardButton("✨ Join Channel ✨", url=invite.invite_link))

    markup.add(types.InlineKeyboardButton("• Try Again •", callback_data="check_fsub"))
    bot.reply_to(message, "<b>⚠️ Access Restricted!</b>\nJoin our official channels to view results.", reply_markup=markup, parse_mode="HTML")
