import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ============ Logger ============
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============ Config ============
TOKEN = os.getenv("7890244767:AAE4HRfDjhyLce4feEaK_YCgFaJbVHi_2nA")  # Render এ Environment Variable এ দিতে হবে

# ============ Flask Server ============
server = Flask(__name__)

@server.route("/")
def home():
    return "✅ Bot is running on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    server.run(host="0.0.0.0", port=port)

# ============ Telegram Bot ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot is working fine!")

def main():
    if not TOKEN:
        raise RuntimeError("❌ Please set BOT_TOKEN in environment!")

    # Flask আলাদা থ্রেডে চালানো হচ্ছে
    threading.Thread(target=run_flask).start()

    # Telegram bot চালু
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    logger.info("🤖 Bot started polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
