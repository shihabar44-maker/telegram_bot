from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# 👉 এখানে তোমার BotFather থেকে পাওয়া Token বসাও
TOKEN = "8386188290:AAEW2I-fBiWr-goPDaVamm39VmGR6WuKZ-A"

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

def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("tips", tips))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
