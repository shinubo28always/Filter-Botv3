import time
from bot_instance import bot
import config
from utils import send_log

# Import Plugins (Taaki handlers register ho jayein)
import plugins.auth
import plugins.setup
import plugins.search
import plugins.commands

if __name__ == "__main__":
    print("🚀 Bot Started with MongoDB Support...")
    send_log("<b>Bot is Online!</b> Moduler structure active.")
    bot.infinity_polling()
