from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 👉 এখানে তোমার BotFather থেকে পাওয়া টোকেন বসাও
TOKEN = "8386188290:AAHTsdQo--lJwyxCaoxN9R-BCj-XcEa4fKM"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 MY Account", "💬 Support Group 💬"],
        ["✨💥Referral💥✨", "💵 Balance 💯"],
        ["⚠️ Rules ⚠️", "✅Withdraw💯"],
        ["❗🔥 How do you do income 🔥❓", "✨🟢Live_Chat_Admin🟢✨"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "⚡ স্বাগতম! আমি তোমার Telegram Bot.\n\n👇 নিচের মেনু থেকে একটি বেছে নাও:",
        reply_markup=reply_markup
    )

# যখন কোনো button চাপা হবে
async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💵 Balance 💯":
        await update.message.reply_text("💰 তোমার Balance হলো: 1000 টাকা")
    elif text == "⚠️ Rules ⚠️":
        await update.message.reply_text("⚠️ পেমেন্ট পেতে হলে অবশ্যই আমাদের গ্রুপে জয়েন থাকতে হবে:\n👉 https://t.me/referearn_20")
    elif text == "✅Withdraw💯":
        await update.message.reply_text("✅ Withdraw করতে হলে Admin এর সাথে যোগাযোগ করুন।")
    elif text == "✨💥Referral💥✨":
        await update.message.reply_text("🔗 তোমার রেফারেল লিংক: https://t.me/YourBot?start=ref123")
    elif text == "💰 MY Account":
        await update.message.reply_text("📂 তোমার একাউন্টের বিস্তারিত এখানে দেখানো হবে।")
    elif text == "💬 Support Group 💬":
        await update.message.reply_text("👉 আমাদের সাপোর্ট গ্রুপ: https://t.me/YourSupportGroup")
    elif text == "❗🔥 How do you do income 🔥❓":
        await update.message.reply_text("💡 এখানে আয়ের নিয়ম দেওয়া হবে।")
    elif text == "✨🟢Live_Chat_Admin🟢✨":
        await update.message.reply_text("🔔 Admin এর সাথে যোগাযোগ করো: https://t.me/YourAdminUsername")
    else:
        await update.message.reply_text("❌ Invalid Option, আবার চেষ্টা করো।")

# Main function
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
