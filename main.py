import os
from flask import Flask, request
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "8386188290:AAEW2I-fBiWr-goPDaVamm39VmGR6WuKZ-A"
bot = Bot(token=TOKEN)

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 MY Account", "💬 Support"],
        ["✨💥Referral💥✨", "💵 Balance"],
        ["⚠️ Rules ⚠️", "✅ Withdraw 💯"],
        ["❗🔥 How do you do income 🔥❗"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        "হ্যালো 👋 আমি চালু আছি!\n\nনিচের মেনু থেকে যেকোনো একটি বেছে নাও 👇",
        reply_markup=reply_markup
    )

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ এখানে তুমি বাটন ব্যবহার করে Account, Balance, Support ইত্যাদি দেখতে পারবে।"
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

# Menu button handler
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 MY Account":
        await update.message.reply_text("👤 এটি তোমার Account সেকশন।")
    elif text == "💬 Support":
        await update.message.reply_text("☎️ আমাদের সাথে যোগাযোগ করতে এখানে লিখুন 👉 @YourSupport")
    elif text == "✨💥Referral💥✨":
        await update.message.reply_text("🔗 তোমার Referral Link এখানে থাকবে।")
    elif text == "💵 Balance":
        await update.message.reply_text("💰 তোমার বর্তমান Balance: 0.00৳")
    elif text == "⚠️ Rules ⚠️":
        await update.message.reply_text("📜 এখানে সব নিয়মাবলী লেখা থাকবে।")
    elif text == "✅ Withdraw 💯":
        await update.message.reply_text("💸 Withdraw করার জন্য লিঙ্কে ক্লিক করুন।")
    elif text == "❗🔥 How do you do income 🔥❗":
        await update.message.reply_text("💡 এখানে ইনকামের বিস্তারিত লেখা থাকবে।")
    else:
        await update.message.reply_text("❌ আমি বুঝতে পারলাম না, অনুগ্রহ করে মেনু থেকে নির্বাচন করুন।")

# Handler যোগ করা হলো
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("about", about))
application.add_handler(CommandHandler("tips", tips))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

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
