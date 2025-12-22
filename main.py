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

# Plugins Load Hone ka confirmation print karein
print("⚙️ Loading Modules...")
import plugins.commands
import plugins.request
import plugins.broadcast
import plugins.auth
import plugins.setup
import plugins.search
print("⚙️ Modules Loaded!")

app = Flask(__name__)
@app.route('/')
def health(): return "Bot is Alive", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Conflict aur Purane updates clear karein
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(2) 
    
    print(f"🚀 Bot Started | Owner: {config.OWNER_ID}")
    
    # Send Log ONLY after polling starts
    try:
        send_log("<b>Bot is Online & Polling!</b>")
    except: pass
    
    while True:
        try:
            # infinity_polling ko simple rakhein
            bot.infinity_polling(
                timeout=60, 
                long_polling_timeout=20,
                allowed_updates=['message', 'callback_query', 'chat_member', 'my_chat_member', 'channel_post']
            )
        except Exception as e:
            print(f"⚠️ Polling Error: {e}")
            time.sleep(5)
