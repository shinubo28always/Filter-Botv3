### This bot is Created By UNRATED CODER --- Please Join & Support @UNRATED_CODER ###
### ==========================★========================== ###
### ---------- Created By UNRATED CODER ™ TEAM ---------- ###
###  Join on Telegram Channel https://t.me/UNRATED_CODER  ###
### ==========================★========================== ###

import time
import threading
import config
import database as db
from bot_instance import bot
from telebot import types, apihelper
from thefuzz import process, fuzz

# ---------------- SETTINGS ----------------
ITEMS_PER_PAGE = 5   
FUZZY_THRESHOLD = 80 

# Background Deletion Engine
def delete_msg_timer(chat_id, message_ids, delay):
    def delayed_delete():
        time.sleep(delay)
        for m_id in message_ids:
            try: bot.delete_message(chat_id, m_id)
            except: pass
    threading.Thread(target=delayed_delete).start()

# ---------------- MESSAGE HANDLER ----------------
@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    if message.text.startswith("/"): return
    uid = message.from_user.id
    db.add_user(uid)
    query = message.text.lower().strip()

    # 1. FSUB CHECK (ONLY PM)
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

    # 2. ALPHABET INDEX SYSTEM
    if len(query) == 1 and query.isalpha():
        wait_msg = bot.reply_to(message, f"🔍 <b>Indexing '{query.upper()}'... Please wait.</b>")
        send_index_page(message.chat.id, query, 1, message.message_id, uid, edit_mid=wait_msg.message_id)
        return

    # 3. SEARCH ENGINE
    choices = db.get_all_keywords()
    if not choices: return
    matches = process.extract(query, choices, limit=15, scorer=fuzz.token_sort_ratio)
    best_matches = [m for m in matches if m[1] >= FUZZY_THRESHOLD]
    
    if not best_matches:
        if message.chat.type == "private":
            bot.reply_to(message, "❌ <b>No results found!</b> Please check spelling or try another anime name")
        return

    # Case A: Exact Match
    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
        return

    # Case B: Suggestions
    markup = types.InlineKeyboardMarkup()
    seen_titles = set()
    for b in best_matches:
        row = db.get_filter(b[0])
        if row and row['title'] not in seen_titles:
            f_type = "S" if row.get('type') == 'slot' else "A"
            src_cid = row.get('source_cid', 0)
            cb = f"res|{f_type}|{row['db_mid']}|{src_cid}|{uid}|{message.message_id}"
            markup.add(types.InlineKeyboardButton(f"🎬 {row['title']}", callback_data=cb))
            seen_titles.add(row['title'])
            if len(seen_titles) >= 5: break 

    if seen_titles:
        s_msg = bot.reply_to(message, "🧐 <b>Did you mean:</b>", reply_markup=markup)
        delete_msg_timer(message.chat.id, [s_msg.message_id], 300)

# ---------------- CALLBACK HANDLER ----------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    data = call.data.split("|")
    clicker_id = call.from_user.id

    if data[0] in ["ind", "res"]:
        searcher_id = int(data[4])
        if clicker_id != searcher_id and not db.is_admin(clicker_id):
            return bot.answer_callback_query(call.id, "⚠️ Oops! That’s not your result. Go to search yourself!", show_alert=True)

    try: bot.answer_callback_query(call.id)
    except: pass

    if data[0] == "ind":
        letter, page, ouid, original_mid = data[1], int(data[2]), int(data[3]), int(data[4])
        send_index_page(call.message.chat.id, letter, page, original_mid, ouid, edit_mid=call.message.message_id)
        return

    if data[0] == "res":
        f_type, db_mid, src_cid, ouid, r_mid = data[1], int(data[2]), int(data[3]), int(data[4]), int(data[5])
        res_data = db.get_filter(process.extractOne(str(db_mid), [str(k['db_mid']) for k in db.filters.find()]) [0]) # Deep Fetch
        # If deep fetch fails, build basic object
        if not res_data:
            res_data = {'type': 'slot' if f_type == "S" else 'anime', 'db_mid': db_mid, 'source_cid': src_cid}
        
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        send_final_result(call.message, res_data, r_mid)

# ---------------- SEND RESULT (FIXED FOR SLOT BUTTONS) ----------------

def send_final_result(message, data, r_mid):
    is_slot = data.get('type') == 'slot'
    del_time = 120 if is_slot else 300 
    
    try:
        markup = types.InlineKeyboardMarkup()
        
        if is_slot:
            # --- CUSTOM SLOT BUTTONS RECONSTRUCTION ---
            custom_btns = data.get('custom_buttons', [])
            for btn in custom_btns:
                markup.add(types.InlineKeyboardButton(btn['name'], url=btn['url']))
            
            res_msg = bot.copy_message(
                chat_id=message.chat.id, 
                from_chat_id=int(config.DB_CHANNEL_ID), 
                message_id=int(data['db_mid']), 
                reply_markup=markup if custom_btns else None, # Yahan buttons wapas add honge
                reply_to_message_id=r_mid
            )
        else:
            # --- ANIME LOGIC ---
            invite = bot.create_chat_invite_link(int(data['source_cid']), member_limit=0)
            markup.add(types.InlineKeyboardButton("🎬 Watch / Download", url=invite.invite_link))
            res_msg = bot.copy_message(
                message.chat.id, 
                int(config.DB_CHANNEL_ID), 
                int(data['db_mid']), 
                reply_markup=markup, 
                reply_to_message_id=r_mid
            )
        
        delete_msg_timer(message.chat.id, [res_msg.message_id, r_mid], del_time)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ <b>Error!</b>\n<code>{str(e)}</code>", reply_to_message_id=r_mid, parse_mode="HTML")

# ---------------- HELPER FUNCTIONS ----------------

def send_index_page(chat_id, letter, page, original_mid, uid, edit_mid=None):
    results = db.get_index_results(letter)
    unique = []
    seen = set()
    for res in results:
        if res['title'] not in seen:
            unique.append(res); seen.add(res['title'])

    if not unique:
        bot.edit_message_text(f"📂 No results for <b>'{letter.upper()}'</b>", chat_id, edit_mid)
        return

    total_pages = (len(unique) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start = (page - 1) * ITEMS_PER_PAGE
    page_items = unique[start:start + ITEMS_PER_PAGE]

    markup = types.InlineKeyboardMarkup()
    for item in page_items:
        f_type = "S" if item.get('type') == 'slot' else "A"
        cb = f"res|{f_type}|{item['db_mid']}|{item.get('source_cid',0)}|{uid}|{original_mid}"
        markup.add(types.InlineKeyboardButton(f"🎬 {item['title']}", callback_data=cb))

    nav = []
    if page > 1: nav.append(types.InlineKeyboardButton("⬅️ Back", callback_data=f"ind|{letter}|{page-1}|{uid}|{original_mid}"))
    nav.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="none"))
    if page < total_pages: nav.append(types.InlineKeyboardButton("Next ➡️", callback_data=f"ind|{letter}|{page+1}|{uid}|{original_mid}"))
    markup.row(*nav)
    bot.edit_message_text(f"📂 <b>Index: '{letter.upper()}'</b>", chat_id, edit_mid, reply_markup=markup)

def send_fsub_message(message, missing_normals, request_fsubs):
    markup = types.InlineKeyboardMarkup()
    for f in missing_normals:
        try:
            invite = bot.create_chat_invite_link(int(f['_id']), expire_date=int(time.time())+120, creates_join_request=False, member_limit=1)
            markup.add(types.InlineKeyboardButton(f"✨ Join Channel ✨", url=invite.invite_link))
        except: pass
    for r in request_fsubs:
        try:
            invite = bot.create_chat_invite_link(int(r['_id']), expire_date=int(time.time())+300, creates_join_request=True)
            markup.add(types.InlineKeyboardButton(f"✨ Request to Join ✨", url=invite.invite_link))
        except: pass
    markup.add(types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN))
    bot.reply_to(message, "<b>⚠️ Access Restricted!</b>\n<blockquote><b>To view search results, please join our official channels.</b></blockquote>", reply_markup=markup, parse_mode="HTML")

### Join & Support Us on Telegram Channel! @UNRATED_CODER ###
