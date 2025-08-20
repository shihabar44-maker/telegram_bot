from flask import Flask, request
from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# 👉 Bot Token বসাও
TOKEN = "8386188290:AAEW2I-fBiWr-goPDaVamm39VmGR6WuKZ-A"

# Flask App
app = Flask(__name__)
bot = Bot(token=TOKEN)

# Telegram Application
application = Application.builder().token(TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 MY Account", "💬 Support"],
        ["✨💥Referral💥✨", "💵 Balance"],
        ["⚠️ Rules ⚠️", "✅ Withdraw 💯"],
        ["❗🔥 How do you do income 🔥❗"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "⚡ স্বাগতম! আমি তোমার Telegram Bot.\n\n👉 নিচের মেনু থেকে বেছে নাও:",
        reply_markup=reply_markup
    )

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "আমি একটা সহকারী Telegram Bot 🤖\n"
        "আমি আপনাকে কি ভাবে সাহায্য করতে পারি?"
    )

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

# Handler Add
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about))
application.add_handler(CommandHandler("tips", tips))

# Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running with Webhook ✅"

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))  # Render এ default port 10000
    app.run(host="0.0.0.0", port=PORT)
