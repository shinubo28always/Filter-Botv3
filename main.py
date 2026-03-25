# Please Support Us! @DogeshBhai_Pure_Bot on Telegram! 
# This Bot Created By: @AniReal_Support!
import os
import sys
import threading
import time
import logging
from flask import Flask

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("AnimeBot")

# Path fix
sys.path.append(os.getcwd())

from bot_instance import bot
import config
import database as db
from utils import send_log

# Import Plugins in specific order
import plugins.admins
import plugins.auth
import plugins.broadcast
import plugins.commands
import plugins.fsub
import plugins.request
import plugins.search
import plugins.setup
import plugins.slots
import plugins.settings

app = Flask(__name__)
@app.route('/')
def health():
    # Check DB connectivity
    try:
        db.db.command('ping')
        return {
            "status": "alive",
            "database": "connected",
            "uptime": time.time() - start_time
        }, 200
    except Exception as e:
        return {"status": "alive", "database": "error", "error": str(e)}, 500

start_time = time.time()

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # 1. Flask Start
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. DATABASE CLEANUP
    try:
        deleted_reqs = db.cleanup_old_requests(30)
        if deleted_reqs: logger.info(f"🧹 Cleaned up {deleted_reqs} old requests.")
    except Exception as e:
        logger.warning(f"Cleanup error: {e}")

    # 2. FORCE CLEANUP
    logger.info("🔄 Clearing sessions and pending updates...")
    try:
        bot.remove_webhook()
        # Drop_pending_updates=True purane saare atke hue messages clear kar dega
        bot.delete_webhook(drop_pending_updates=True) 
        time.sleep(3) # Wait for Telegram to reset
    except Exception as e:
        logger.warning(f"Webhook cleanup warning: {e}")
    
    logger.info(f"🚀 Bot Started | Owner: {config.OWNER_ID}")
    try:
        send_log("<blockquote><b>Bᴏᴛ Sᴛᴀʀᴛᴇᴅ Bʏ: @UNRATED_CODER</b></blockquote>")
    except: pass

    # 3. POLLING WITH BROAD PERMISSIONS
    while True:
        try:
            logger.info("📡 Bot is now polling...")
            bot.infinity_polling(
                timeout=90,
                skip_pending=True,
                allowed_updates=['message', 'callback_query', 'chat_member', 'my_chat_member', 'chat_join_request'],
                logger_level=logging.ERROR
            )
        except Exception as e:
            if "409" in str(e):
                logger.error("🛑 409 CONFLICT: Another bot instance is running with this token!")
                logger.warning("Please stop the other instance or change your API TOKEN.")
                time.sleep(20) # Increase wait on conflict
            else:
                logger.error(f"⚠️ Polling Error: {e}")
                time.sleep(10) # Wait 10s on other errors

# Join & Support Us! @DogeshBhai_Pure_Bot!
