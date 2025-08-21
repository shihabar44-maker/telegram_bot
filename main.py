import os
from flask import Flask, request
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# সরাসরি Token বসানো হলো
TOKEN = "8386188290:AAEW2I-fBiWr-goPDaVamm39VmGR6WuKZ-A"
bot = Bot(TOKEN)

# Flask app
app = Flask(__name__)

# Telegram Application
application = Application.builder().token(TOKEN).build()

# ---------- Commands ----------
# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 MY Account", "💬 Support"],
        ["✨💥Referral💥✨", "💵 Balance"],
        ["⚠️ Rules ⚠️", "✅ Withdraw 💯"],
        ["❗🔥 How do you do income 🔥❗"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "হ্যালো 👋 আমি চালু আছি!\nনিচের মেনু থেকে যেকোনো একটি বেছে নাও:",
        reply_markup=reply_markup
    )

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("আমি তোমাকে সাহায্য করার জন্য এখানে আছি! 😊")

# /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "আমার নিজের হাতে তৈরি একটি ছোট্ট সহকারী — সবসময় প্রস্তুত তোমার কাজে সাহায্য করার জন্য!"
    )

# /tips
async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "আমার সম্পর্কে আরো জানতে চাইলে ক্লিক করুন 👉 https://t.me/sr_sadiya_official"
    )

# ---------- Text Button Handler ----------
async def button_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 MY Account":
        await update.message.reply_text("🧾 তোমার অ্যাকাউন্টের তথ্য এখানে!")
    elif text == "💬 Support":
        await update.message.reply_text("📩 সাপোর্টে যোগাযোগ করুন: @YourSupportID")
    elif text == "💵 Balance":
        await update.message.reply_text("💸 তোমার বর্তমান ব্যালেন্স: 0৳")
    elif text == "✨💥Referral💥✨":
        await update.message.reply_text("🔗 তোমার রেফারেল লিংক: https://t.me/YourBot?start=ref123")
    elif text == "⚠️ Rules ⚠️":
        await update.message.reply_text("📜 নিয়মাবলী: এখানে নিয়ম লেখা থাকবে।")
    elif text == "✅ Withdraw 💯":
        await update.message.reply_text("✅ ন্যূনতম ৫০৳ হলে তুমি উইথড্র করতে পারো।")
    elif text == "❗🔥 How do you do income 🔥❗":
        await update.message.reply_text("🎁 ইনকাম করার নিয়ম: বন্ধুদের রেফার করো, বোনাস পাও!")
    else:
        await update.message.reply_text("❓ আমি এই টেক্সট চিনতে পারিনি।")

# ---------- Handlers ----------
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about))
application.add_handler(CommandHandler("tips", tips))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_response))

# ---------- Webhook Routes ----------
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "Bot is running with Webhook ✅"

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))  # Render default port 10000
    app.run(host="0.0.0.0", port=PORT)
