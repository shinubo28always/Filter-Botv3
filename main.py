# Please Support Us! @DogeshBhai_Pure_Bot on Telegram! 
# This Bot Created By: @AniReal_Support!
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

# Import Plugins in specific order
import plugins.commands
import plugins.admins
import plugins.fsub
import plugins.request
import plugins.broadcast
import plugins.auth
import plugins.setup
import plugins.slots
import plugins.search

app = Flask(__name__)
@app.route('/')
def health(): return "Bot is Alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # 1. Flask Start
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. FORCE CLEANUP
    print("🔄 Clearing sessions and pending updates...")
    try:
        bot.remove_webhook()
        # Drop_pending_updates=True purane saare atke hue messages clear kar dega
        bot.delete_webhook(drop_pending_updates=True) 
        time.sleep(3) # Wait for Telegram to reset
    except: pass
    
    print(f"🚀 Bot Started | Owner: {config.OWNER_ID}")
    try:
        send_log("<blockquote><b>Bᴏᴛ Sᴛᴀʀᴛᴇᴅ Bʏ: @UNRATED_CODER</b></blockquote>")
    except: pass

    # 3. POLLING WITH BROAD PERMISSIONS
    while True:
        try:
            bot.infinity_polling(
                timeout=60, 
                skip_pending=True,
                allowed_updates=['message', 'callback_query', 'chat_member', 'my_chat_member', 'chat_join_request']
            )
        except Exception as e:
            print(f"⚠️ Polling Error: {e}")
            time.sleep(10) # Conflict hone par 10s wait

# Join & Support Us! @DogeshBhai_Pure_Bot!
