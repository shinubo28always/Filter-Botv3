import os
import sys
import threading
import time
from flask import Flask
from bot_instance import bot
import config
from utils import send_log

sys.path.append(os.getcwd())

# Import Order
import plugins.commands
import plugins.request
import plugins.broadcast
import plugins.auth
import plugins.setup
import plugins.search

app = Flask(__name__)
@app.route('/')
def health(): return "Active", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    
    # --- CONFLICT FIX ---
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(1) 
    
    print("🚀 Bot Started Successfully!")
    send_log("<b>Bot is Online!</b>")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, allowed_updates=['message', 'callback_query', 'chat_member', 'my_chat_member'])
        except Exception as e:
            time.sleep(5)
