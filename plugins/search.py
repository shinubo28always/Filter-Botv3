### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
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
        if missing:
            return send_fsub_message(message, missing, [f for f in all_fsubs if f.get("mode") == "request"])

    # 2. ALPHABET INDEX (NOW FAST)
    if len(query) == 1 and query.isalpha():
        wait_msg = bot.reply_to(message, f"🔍 <b>Indexing '{query.upper()}'...</b>")
        send_index_page(message.chat.id, query, 1, message.message_id, uid, edit_mid=wait_msg.message_id)
        return

    # 3. SEARCH ENGINE
    choices = db.get_all_keywords()
    if not choices: return
    matches = process.extract(query, choices, limit=15, scorer=fuzz.token_sort_ratio)
    best_matches = [m for m in matches if m[1] >= FUZZY_THRESHOLD]
    
    if not best_matches:
        if message.chat.type == "private":
            bot.reply_to(message, "❌ <b>No results found!</b>")
        return

    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
        return

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
        s_msg = bot.reply_to(message, "🧐 <b>Did you mean:</b>", reply_markup=markup)
        delete_msg_timer(message.chat.id, [s_msg.message_id], 300)

def send_index_page(chat_id, letter, page, original_mid, uid, edit_mid=None):
    results = db.get_index_results(letter)
    unique_results = []
    seen_titles = set()
    for res in results:
        if res['title'] not in seen_titles:
            unique_results.append({"kw": res['keyword'], "title": res['title']})
            seen_titles.add(res['title'])

    if not unique_results:
        bot.edit_message_text(f"📂 No results for <b>'{letter.upper()}'</b>", chat_id, edit_mid)
        return

    total_pages = (len(unique_results) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = (page - 1) * ITEMS_PER_PAGE
    page_items = unique_results[start:start + ITEMS_PER_PAGE]

    markup = types.InlineKeyboardMarkup()
    for item in page_items:
        markup.add(types.InlineKeyboardButton(f"🎬 {item['title']}", callback_data=f"fuz|{item['kw'][:20]}|{original_mid}|{uid}"))

    nav_row = []
    if page > 1: nav_row.append(types.InlineKeyboardButton("⬅️ Back", callback_data=f"ind|{letter}|{page-1}|{uid}|{original_mid}"))
    nav_row.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="none"))
    if page < total_pages: nav_row.append(types.InlineKeyboardButton("Next ➡️", callback_data=f"ind|{letter}|{page+1}|{uid}|{original_mid}"))
    markup.row(*nav_row)

    bot.edit_message_text(f"📂 <b>Anime Index: '{letter.upper()}'</b>", chat_id, edit_mid, reply_markup=markup)

# This is called from slots.py callback handler to maintain speed
def handle_callbacks(call):
    clicker_id = call.from_user.id
    data = call.data.split("|")
    
    if data[0] in ["ind", "fuz"]:
        original_uid = int(data[3])
        if clicker_id != original_uid and not db.is_admin(clicker_id):
            return bot.answer_callback_query(call.id, "⚠️ Search yourself @UNRATED_CODER", show_alert=True)
        
        bot.answer_callback_query(call.id) # Fast response
        
        if data[0] == "ind":
            send_index_page(call.message.chat.id, data[1], int(data[2]), int(data[4]), original_uid, edit_mid=call.message.message_id)
        elif data[0] == "fuz":
            filter_data = db.get_filter(data[1])
            if filter_data:
                try: bot.delete_message(call.message.chat.id, call.message.message_id)
                except: pass
                send_final_result(call.message, filter_data, int(data[2]))

def send_final_result(message, data, r_mid):
    is_slot = data.get('type') == 'slot'
    del_time = 120 if is_slot else 300 
    try:
        markup = types.InlineKeyboardMarkup()
        if is_slot:
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
    bot.reply_to(message, "⚠️ <b>Access Restricted!</b>\nJoin our channels to view results.", reply_markup=markup)
