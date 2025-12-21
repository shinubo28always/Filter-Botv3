import os
import threading
from flask import Flask
from bot_instance import bot
import config
from utils import send_log

# Plugins import 
import plugins.auth
import plugins.setup
import plugins.search
import plugins.commands

# --- FLASK SERVER SETUP (For Render/Heroku) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Alive!", 200

def run_flask():
    # Render automatically PORT environment variable deta hai
    port = int(os.environ.get("PORT", 8080))
    # host='0.0.0.0' zaroori hai Render ke liye
    app.run(host='0.0.0.0', port=port)

# --- BOT START LOGIC ---
if __name__ == "__main__":
    if not config.API_TOKEN:
        print("❌ ERROR: API_TOKEN missing in config or environment!")
        exit()

    # 1. Flask ko alag thread mein start karein
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    print(f"🌐 Flask Server started on port {os.environ.get('PORT', 8080)}")
    print(f"🚀 Bot is Polling | Owner: {config.OWNER_ID}")
    
    # Bot startup alert
    try:
        send_log(f"<b>Bot Started!</b>\nHealth Check: Active on Port {os.environ.get('PORT', 8080)}")
    except:
        pass

    # 2. Bot Infinity Polling start karein
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=5)
        except Exception as e:
            print(f"⚠️ Polling Error: {e}")
            import time
            time.sleep(5)
