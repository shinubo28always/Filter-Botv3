### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

import time, threading, config, database as db
from bot_instance import bot
from telebot import types, apihelper
from thefuzz import process, fuzz

ITEMS_PER_PAGE = 5   
FUZZY_THRESHOLD = 80 

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
    db.add_user(uid)
    query = message.text.lower().strip()

    # 1. FSUB CHECK
    if message.chat.type == "private":
        all_fsubs = db.get_all_fsub()
        missing = []
        for f in all_fsubs:
            if f.get("mode") == "request": continue
            try:
                st = bot.get_chat_member(int(f['_id']), uid).status
                if st not in ['member', 'administrator', 'creator']: missing.append(f)
            except: missing.append(f)
        if missing: return send_fsub_message(message, missing, [f for f in all_fsubs if f.get("mode") == "request"])

    # 2. ALPHABET INDEX (NOW FIXED)
    if len(query) == 1 and query.isalpha():
        wait_msg = bot.reply_to(message, f"🔍 <b>Searching for '{query.upper()}'...</b>")
        send_index_page(message.chat.id, query, 1, message.message_id, uid, edit_mid=wait_msg.message_id)
        return

    # 3. KEYWORD SCANNING (Slots)
    all_kws = db.get_all_keywords()
    for word in query.split():
        data = db.get_filter(word)
        if data and data.get('type') == 'slot':
            return send_final_result(message, data, message.message_id)

    # 4. FUZZY SEARCH
    matches = process.extract(query, all_kws, limit=10, scorer=fuzz.token_sort_ratio)
    best_matches = [m for m in matches if m[1] >= FUZZY_THRESHOLD]
    if not best_matches:
        if message.chat.type == "private": bot.reply_to(message, "❌ <b>No results found!</b>")
        return

    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
    else:
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
            delete_msg_timer(message.chat.id, [s_msg.message_id], 300)

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
    try: bot.edit_message_text(text, chat_id, edit_mid, reply_markup=markup)
    except: pass

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    data = call.data.split("|")
    if data[0] in ["ind", "res"]:
        searcher_id = int(data[4]) if data[0] == "ind" else int(data[2])
        if call.from_user.id != searcher_id and not db.is_admin(call.from_user.id):
            return bot.answer_callback_query(call.id, "⚠️ Not your request!", show_alert=True)

    bot.answer_callback_query(call.id)
    if data[0] == "ind":
        send_index_page(call.message.chat.id, data[1], int(data[2]), int(data[4]), int(data[3]), edit_mid=call.message.message_id)
    elif data[0] == "res":
        filter_data = db.get_filter_by_mid(int(data[1]))
        if filter_data:
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            send_final_result(call.message, filter_data, int(data[3]))

def send_final_result(message, data, r_mid):
    is_slot = data.get('type') == 'slot'
    del_time = 120 if is_slot else 300 
    try:
        markup = types.InlineKeyboardMarkup()
        if is_slot:
            # Custom buttons support
            for btn in data.get('custom_buttons', []): markup.add(types.InlineKeyboardButton(btn['name'], url=btn['url']))
            res_msg = bot.copy_message(message.chat.id, int(config.DB_CHANNEL_ID), int(data['db_mid']), reply_markup=markup if data.get('custom_buttons') else None, reply_to_message_id=r_mid)
        else:
            invite = bot.create_chat_invite_link(int(data['source_cid']), member_limit=0)
            markup.add(types.InlineKeyboardButton("🎬 Watch / Download", url=invite.invite_link))
            res_msg = bot.copy_message(message.chat.id, int(config.DB_CHANNEL_ID), int(data['db_mid']), reply_markup=markup, reply_to_message_id=r_mid)
        delete_msg_timer(message.chat.id, [res_msg.message_id, r_mid], del_time)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>Error!</b>\n<code>{str(e)}</code>", reply_to_message_id=r_mid)

def send_fsub_message(message, missing, request_fsubs):
    markup = types.InlineKeyboardMarkup()
    for f in missing:
        invite = bot.create_chat_invite_link(int(f['_id']), expire_date=int(time.time())+120, member_limit=1)
        markup.add(types.InlineKeyboardButton(f"✨ Join Channel ✨", url=invite.invite_link))
    for r in request_fsubs:
        invite = bot.create_chat_invite_link(int(r['_id']), expire_date=int(time.time())+300, creates_join_request=True)
        markup.add(types.InlineKeyboardButton(f"✨ Request to Join ✨", url=invite.invite_link))
    markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))
    bot.reply_to(message, "<b>⚠️ Access Restricted!</b>\nJoin our official channels to view results.", reply_markup=markup, parse_mode="HTML")
