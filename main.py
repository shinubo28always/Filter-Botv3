import os
import sys
import threading
import time
from flask import Flask

# Path fix: Render par modular imports sahi se chalein iske liye zaroori hai
sys.path.append(os.getcwd())

from bot_instance import bot
import config
from utils import send_log

# ==========================================
# 👇 IMPORT PLUGINS (ORDER IS CRITICAL)
# ==========================================
# Sabse pehle commands aur broadcast ko load karein
# Phir auth aur setup, aur sabse aakhir mein Search
# kyunki search saare messages ko catch kar leta hai.

print("DEBUG: Loading Plugins...")
try:
    import plugins.commands
    import plugins.request
    import plugins.broadcast
    import plugins.auth
    import plugins.setup
    import plugins.search  # Search hamesha last mein hona chahiye
    print("✅ All Plugins Loaded Successfully!")
except Exception as e:
    print(f"❌ Plugin Loading Error: {e}")

# ==========================================
# 👇 FLASK SERVER (For Render Health Check)
# ==========================================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Running!", 200

def run_flask():
    # Render automatically 'PORT' variable provide karta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 👇 MAIN BOT EXECUTION
# ==========================================
if __name__ == "__main__":
    if not config.API_TOKEN:
        print("❌ ERROR: API_TOKEN is missing in config/env!")
        sys.exit()

    # 1. Flask ko background thread mein start karein
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print(f"🌐 Flask Server started on port {os.environ.get('PORT', 8080)}")

    # 2. ANTI-CONFLICT LOGIC
    # Purane sessions aur pending messages ko clear karna
    print("🔄 Cleaning up old sessions and conflicts...")
    try:
        bot.remove_webhook()
        bot.delete_webhook(drop_pending_updates=True)
        time.sleep(2) # Telegram servers ko reset hone ka waqt dein
    except Exception as e:
        print(f"⚠️ Cleanup Warning: {e}")

    print(f"🚀 Bot is Polling | Owner ID: {config.OWNER_ID}")
    
    # Startup Alert (Log Channel mein)
    try:
        send_log("<b>Bot Started Successfully!</b>\nAll conflicts cleared and modules active.")
    except:
        pass

    # 3. INFINITY POLLING (Safe Loop)
    while True:
        try:
            bot.infinity_polling(
                timeout=60, 
                long_polling_timeout=20, 
                skip_pending=True, # Purane messages ignore karein
                allowed_updates=['message', 'callback_query', 'chat_member', 'my_chat_member']
            )
        except Exception as e:
            # Agar koi network error aaye toh 5 second baad auto-restart hoga
            print(f"⚠️ Polling Error: {e}")
            time.sleep(5)
