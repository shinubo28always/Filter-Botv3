import os
import sys
import threading
import time
from flask import Flask

sys.path.append(os.getcwd())
from bot_instance import bot
import config
from utils import send_log

import plugins.commands
import plugins.request
import plugins.broadcast
import plugins.auth
import plugins.setup
import plugins.search

app = Flask(__name__)
@app.route('/')
def health(): return "OK", 200

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    
    # --- HARD RESET ---
    print("🔄 Killing old sessions...")
    try:
        bot.stop_polling()
        time.sleep(2)
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(3) # Telegram API ko reset hone ka time dein
    except: pass

    print(f"🚀 Bot Online | ID: {config.OWNER_ID}")
    
    while True:
        try:
            bot.infinity_polling(
                timeout=90, 
                long_polling_timeout=20,
                skip_pending=True,
                allowed_updates=['message', 'callback_query', 'chat_member', 'my_chat_member']
            )
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)
