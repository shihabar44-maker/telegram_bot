from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 👉 এখানে তোমার BotFather থেকে পাওয়া Token বসাও
TOKEN = "8386188290:AAEW2I-fBiWr-goPDaVamm39VmGR6WuKZ-A"


# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 MY Account", "💬 Support Group 💬"],
        ["✨💥Referral💥✨", "💵 Balance 💯"],
        ["⚠️ Rules ⚠️", "✅ Withdraw 💯"],
        ["❗🔥 How do you do income 🔥❗", "✨🟢 Live_Chat_Admin 🟢✨"]
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

# বাটন চাপলে রিপ্লাই
async def button_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 MY Account":
        await update.message.reply_text("🧾 এখানে তোমার একাউন্ট ডিটেইলস থাকবে।")
    elif text == "💬 Support Group 💬":
        await update.message.reply_text("📢 আমাদের Support Group এ যোগ দাও 👉 https://t.me/your_support_group")
    elif text == "✨💥Referral💥✨":
        await update.message.reply_text("👥 তোমার Referral লিঙ্ক শেয়ার করো এবং ইনকাম করো!")
    elif text == "💵 Balance 💯":
        await update.message.reply_text("💵 তোমার ব্যালেন্স এখন 0.00৳")
    elif text == "⚠️ Rules ⚠️":
        await update.message.reply_text("📜 নিয়মাবলী:\n1. Spam কোরো না\n2. নিয়ম মেনে ব্যবহার করো")
    elif text == "✅ Withdraw 💯":
        await update.message.reply_text("💳 Withdraw করতে Support এর সাথে যোগাযোগ করো।")
    elif text == "❗🔥 How do you do income 🔥❗":
        await update.message.reply_text("💡 ইনকাম করার টিপস শিগগিরই আসছে!")
    elif text == "✨🟢 Live_Chat_Admin 🟢✨":
        await update.message.reply_text("👩‍💻 সরাসরি অ্যাডমিনের সাথে কথা বলো 👉 @your_admin_username")

def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("tips", tips))

    # Button response
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_response))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
