import sys
import os
import threading
import time
from flask import Flask

# Path fix for Render
sys.path.append(os.getcwd())

from bot_instance import bot
import config
from utils import send_log

# 1. PEHLE COMMANDS IMPORT KAREIN
print("DEBUG: Loading Commands...")
import plugins.commands

# 2. PHIR AUTH AUR SETUP
print("DEBUG: Loading Auth & Setup...")
import plugins.auth
import plugins.setup

# 3. SABSE LAST MEIN SEARCH
print("DEBUG: Loading Search...")
import plugins.search

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    if not config.API_TOKEN:
        print("❌ CRITICAL ERROR: API_TOKEN is empty!")
        exit()

    # Flask Thread
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Conflict Clear
    bot.delete_webhook(drop_pending_updates=True)
    print(f"🚀 Bot Started Successfully! ID: {config.OWNER_ID}")

    while True:
        try:
            # infinity_polling with all allowed updates
            bot.infinity_polling(
                timeout=60, 
                long_polling_timeout=20, 
                allowed_updates=['message', 'callback_query', 'chat_member', 'my_chat_member', 'channel_post']
            )
        except Exception as e:
            print(f"⚠️ Polling Error: {e}")
            time.sleep(5)
