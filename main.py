import os
import sys
import threading
import time
from flask import Flask

# Path fix
sys.path.append(os.getcwd())

from bot_instance import bot
import config
from utils import send_log

# Import Plugins
import plugins.commands
import plugins.request
import plugins.broadcast
import plugins.auth
import plugins.setup
import plugins.search

app = Flask(__name__)
@app.route('/')
def health(): return "Bot Alive", 200

def run_flask():
    try:
        port = int(os.environ.get("PORT", 8080))
        app.run(host='0.0.0.0', port=port)
    except: pass

if __name__ == "__main__":
    if not config.API_TOKEN:
        print("❌ API_TOKEN missing!")
        sys.exit(1)

    # Flask Thread
    threading.Thread(target=run_flask, daemon=True).start()
    
    # --- HARD RESET ---
    print("🔄 Clearing sessions...")
    try:
        bot.remove_webhook()
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(3) # Wait for Telegram servers
    except: pass

    print(f"🚀 Bot Started | ID: {config.OWNER_ID}")
    try: send_log("<b>Bot is Online!</b>")
    except: pass

    # --- STABLE POLLING LOOP ---
    while True:
        try:
            bot.infinity_polling(
                timeout=60, 
                long_polling_timeout=20,
                skip_pending=True,
                allowed_updates=['message', 'callback_query', 'chat_member', 'my_chat_member']
            )
        except Exception as e:
            print(f"⚠️ Polling Exception: {e}")
            # Agar conflict ho, toh bot 10 second wait karega restart karne se pehle
            time.sleep(10)
