from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Owner ID
OWNER_ID = 8028396521   # এখানে তোমার Telegram numeric ID বসাও

# Keyboard Layout
main_menu = [
    ["💰 My Account", "📢 Referral"],
    ["✅ Withdraw", "💵 Balance"],
    ["💬 Support", "⚠️ Rules"],
    ["🔥 Income Tips"]
]

reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Welcome! Choose an option:",
        reply_markup=reply_markup
    )

# Example Handlers
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 My Account":
        await update.message.reply_text("👤 This is your account info.", reply_markup=reply_markup)

    elif text == "📢 Referral":
        await update.message.reply_text("🔗 Your referral link: https://t.me/YourBot?start=ref123", reply_markup=reply_markup)

    elif text == "✅ Withdraw":
        await update.message.reply_text("✅ Minimum 100৳ হলে Withdraw করতে পারবে।", reply_markup=reply_markup)

    elif text == "💵 Balance":
        await update.message.reply_text("💵 তোমার বর্তমান ব্যালেন্স: 0৳", reply_markup=reply_markup)

    elif text == "💬 Support":
        await update.message.reply_text("📩 সাপোর্ট: @YourSupportID", reply_markup=reply_markup)

    elif text == "⚠️ Rules":
        await update.message.reply_text("⚠️ Rule 1...\n⚠️ Rule 2...", reply_markup=reply_markup)

    elif text == "🔥 Income Tips":
        await update.message.reply_text("🔥 Earn tips will be here.", reply_markup=reply_markup)

# Main Function
def main():
    app = Application.builder().token("8422229356:AAGHAdJCFZNmgNAhx5CchxrM51U53oOc0Ec").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
