from bot_instance import bot
import config
from utils import send_log

# Plugin Imports (Handlers register karne ke liye)
import plugins.auth
import plugins.setup
import plugins.search
import plugins.commands

if __name__ == "__main__":
    if not config.API_TOKEN:
        print("❌ ERROR: API_TOKEN nahi mila! Config check karein.")
        exit()
        
    print(f"🚀 Bot Started | Owner: {config.OWNER_ID}")
    send_log(f"<b>Bot is Online!</b>\nConnected to MongoDB.")
    
    bot.infinity_polling(timeout=60, long_polling_timeout=5)
