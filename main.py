import sys
import os
import threading
from flask import Flask
from bot_instance import bot
import config
from utils import send_log

# Import Order is CRITICAL here
import plugins.commands  # 1. Commands sabse pehle
import plugins.auth      # 2. Auth handlers
import plugins.setup     # 3. Setup flow
import plugins.search    # 4. Search (Sabse last kyunki ye text catch karta hai)

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Conflict fix
    bot.delete_webhook(drop_pending_updates=True)
    
    print(f"🚀 Bot Started | Owner: {config.OWNER_ID}")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=5)
        except Exception as e:
            import time
            time.sleep(5)
