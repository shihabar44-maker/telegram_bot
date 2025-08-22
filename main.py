from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# User data dictionary (balance store করার জন্য)
user_data = {}

# Keyboard Layout
main_menu = [
    ["🏦 Accounts Sell", "💬 Support Group"],
    ["➕ Get 20৳ Balance"]
]

reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # যদি নতুন ইউজার হয়, তার জন্য balance initialize
    if user.id not in user_data:
        user_data[user.id] = {"balance": 0}

    await update.message.reply_text(
        "✨ Welcome! Choose an option:",
        reply_markup=reply_markup
    )

# Handle menu clicks
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    # Accounts Sell
    if text == "🏦 Accounts Sell":
        await update.message.reply_text("🔢 এখানে আপনার account sell সম্পর্কিত তথ্য আসবে।")

    # Support Group
    elif text == "💬 Support Group":
        await update.message.reply_text("💬 আমাদের Support Group এ জয়েন করুন:\n👉 https://t.me/YourSupportGroupLink")

    # Get 20৳ Balance
    elif text == "➕ Get 20৳ Balance":
        user_data[user.id]["balance"] += 20
        balance = user_data[user.id]["balance"]
        await update.message.reply_text(f"🎉 সফলভাবে ২০৳ যোগ হয়েছে!\n💰 আপনার মোট Balance: {balance}৳")

# Main Function
def main():
    app = Application.builder().token("8331378652:AAHiopSQE7WLTQzVdifQNdTQ085GXuKXt5I").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
