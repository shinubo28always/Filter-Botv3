import os
import sys
import threading
import time
from flask import Flask

sys.path.append(os.getcwd())
from bot_instance import bot
import config
from utils import send_log

# IMPORT ORDER (Commands First, Search Last)
import plugins.commands
import plugins.request
import plugins.broadcast
import plugins.auth
import plugins.setup
import plugins.search

app = Flask(__name__)
@app.route('/')
def health(): return "OK", 200

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080))), daemon=True).start()
    
    bot.remove_webhook()
    bot.delete_webhook(drop_pending_updates=True)
    time.sleep(2)
    
    print("🚀 Bot Started Successfully!")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, allowed_updates=['message', 'callback_query', 'chat_member', 'my_chat_member'])
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
