import time
import config
import database as db
from bot_instance import bot
from telebot import types
from thefuzz import process


@bot.message_handler(func=lambda m: True, content_types=['text'])
def search_handler(message):
    if message.text.startswith("/"):
        return

    uid = message.from_user.id
    db.add_user(uid)

    # ---------------- FSUB LOGIC ----------------
    if message.chat.type == "private":
        all_fsubs = db.get_all_fsub()

        normal_fsubs = [f for f in all_fsubs if f.get("mode") != "request"]
        request_fsubs = [f for f in all_fsubs if f.get("mode") == "request"]

        # ---- HARD FSUB CHECK (ONLY NORMAL CHANNELS) ----
        for f in normal_fsubs:
            try:
                member = bot.get_chat_member(int(f['_id']), uid)
                if member.status not in ['member', 'administrator', 'creator']:
                    raise Exception("NOT_JOINED")
            except:
                return send_fsub_message(message, f, request_fsubs)

    # ---------------- SEARCH ENGINE ----------------
    query = message.text.lower().strip()
    choices = db.get_all_keywords()
    if not choices:
        return

    matches = process.extract(query, choices, limit=10)
    best_matches = [m for m in matches if m[1] > 70]
    if not best_matches:
        return

    # Exact match
    if best_matches[0][1] >= 95:
        data = db.get_filter(best_matches[0][0])
        send_final_result(message, data, message.message_id)
        return

    # Suggestions
    markup = types.InlineKeyboardMarkup()
    seen = set()

    for b in best_matches:
        row = db.get_filter(b[0])
        if row and row['title'] not in seen:
            cb = f"fuz|{b[0][:20]}|{message.message_id}|{uid}"
            markup.add(
                types.InlineKeyboardButton(f"🎬 {row['title']}", callback_data=cb)
            )
            seen.add(row['title'])

    if seen:
        bot.reply_to(
            message,
            "🧐 <b>Did you mean:</b>",
            reply_markup=markup,
            parse_mode="HTML"
        )


# ---------------- FORCE JOIN MESSAGE ----------------
def send_fsub_message(message, hard_ch, request_fsubs):
    markup = types.InlineKeyboardMarkup()
    expiry = int(time.time()) + 120  # 2 minutes

    # HARD JOIN BUTTON
    try:
        invite = bot.create_chat_invite_link(
            chat_id=int(hard_ch['_id']),
            expire_date=expiry,
            creates_join_request=False
        )
        markup.add(
            types.InlineKeyboardButton(
                "✨ Join Channel ✨",
                url=invite.invite_link
            )
        )
    except:
        pass

    # OPTIONAL REQUEST CHANNEL BUTTONS (NO CHECK)
    for r in request_fsubs:
        try:
            req_invite = bot.create_chat_invite_link(
                chat_id=int(r['_id']),
                expire_date=expiry,
                creates_join_request=True
            )
            markup.add(
                types.InlineKeyboardButton(
                    "✨ Request To Join ✨",
                    url=req_invite.invite_link
                )
            )
        except:
            pass

    markup.add(
        types.InlineKeyboardButton("📞 Contact Admin", url=config.HELP_ADMIN)
    )

    text = (
        f"<b>⚠️ Access Denied!</b>\n\n"
        f"Bot use karne ke liye pehle "
        f"<b>{hard_ch['title']}</b> join karna hoga.\n\n"
        f"<i>Join karne ke baad dobara search karein.</i>"
    )

    bot.reply_to(
        message,
        text,
        reply_markup=markup,
        parse_mode="HTML"
    )


# ---------------- SEND RESULT ----------------
def send_final_result(message, data, r_mid):
    try:
        invite = bot.create_chat_invite_link(int(data['source_cid']))
        link = invite.invite_link
    except:
        link = config.LINK_ANIME_CHANNEL

    markup = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("🎬 Watch / Download", url=link)
    )

    try:
        bot.copy_message(
            message.chat.id,
            int(config.DB_CHANNEL_ID),
            int(data['db_mid']),
            reply_markup=markup,
            reply_to_message_id=r_mid
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ <b>Error!</b>\n<code>{str(e)}</code>",
            parse_mode="HTML"
        )


# ---------------- CALLBACK HANDLER ----------------
@bot.callback_query_handler(func=lambda call: call.data.startswith("fuz|"))
def handle_fuz_click(call):
    _, key, mid, ouid = call.data.split("|")

    if int(call.from_user.id) != int(ouid) and not db.is_admin(call.from_user.id):
        return bot.answer_callback_query(
            call.id,
            "⚠️ Ye aapka request nahi hai!",
            show_alert=True
        )

    uid = call.from_user.id

    # ONLY NORMAL FSUB CHECK AGAIN
    for f in db.get_all_fsub():
        if f.get("mode") == "request":
            continue
        try:
            st = bot.get_chat_member(int(f['_id']), uid).status
            if st not in ['member', 'administrator', 'creator']:
                return bot.answer_callback_query(
                    call.id,
                    "⚠️ Pehle channel join karein!",
                    show_alert=True
                )
        except:
            return bot.answer_callback_query(
                call.id,
                "⚠️ Pehle channel join karein!",
                show_alert=True
            )

    data = db.get_filter(key) or db.get_filter(
        process.extractOne(key, db.get_all_keywords())[0]
    )

    if data:
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass
        send_final_result(call.message, data, int(mid))
