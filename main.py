import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Bot Token ---
TOKEN = os.environ.get("BOT_TOKEN", "8386188290:AAEW2I-fBiWr-goPDaVamm39VmGR6WuKZ-A")
bot = Bot(token=TOKEN)

# --- Flask app ---
app = Flask(__name__)

# --- Telegram Application ---
application = Application.builder().token(TOKEN).build()

# ---------------- Handlers ---------------- #

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো 👋 আমি চালু আছি!")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("আমি কিছু কমান্ড জানি: /start, /help, /about, /tips")

# /about command
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "আমার নিজের হাতে তৈরি একটি ছোট্ট সহকারী — সবসময় প্রস্তুত তোমার কাজে সাহায্য করার জন্য!"
    )

# /tips command
async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "আমার সম্পর্কে আরো জানতে চাইলে ক্লিক করুন 👉 https://t.me/sr_sadiya_official"
    )

# --- Register handlers ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about))
application.add_handler(CommandHandler("tips", tips))

# ---------------- Webhook Routes ---------------- #

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running with Webhook ✅"

# ---------------- Run Flask ---------------- #

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))  # Render default port = 10000
    app.run(host="0.0.0.0", port=PORT)
