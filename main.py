from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8422229356:AAGHAdJCFZNmgNAhx5CchxrM51U53oOc0Ec"
OWNER_ID = 8028396521   # এখানে তোমার টেলিগ্রাম আইডি বসাও

# --- Start Menu ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👤 My Account", callback_data="account"),
         InlineKeyboardButton("🔗 Referral", callback_data="referral")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
         InlineKeyboardButton("💰 Balance", callback_data="balance")],
        [InlineKeyboardButton("📩 Support", callback_data="support"),
         InlineKeyboardButton("📜 Rules", callback_data="rules")],
        [InlineKeyboardButton("💡 Income Tips", callback_data="tips")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✨ Welcome! Choose an option:", reply_markup=reply_markup)

# --- Button Handler ---
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "account":
        text = f"👤 Your Account Details:\n\n🆔 ID: {query.from_user.id}\n👨 Name: {query.from_user.first_name}\n📛 Username: @{query.from_user.username or 'Not set'}"
        await query.message.reply_text(text)

    elif query.data == "withdraw":
        keyboard = [
            [InlineKeyboardButton("📲 Bkash", callback_data="bkash")],
            [InlineKeyboardButton("💳 Nagad", callback_data="nagad")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
        ]
        await query.message.reply_text("💵 Choose your withdraw method 👇", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "bkash":
        context.user_data["method"] = "Bkash"
        await query.message.reply_text("📲 Please enter your Bkash number:")

    elif query.data == "nagad":
        context.user_data["method"] = "Nagad"
        await query.message.reply_text("💳 Please enter your Nagad number:")

    elif query.data == "back":
        await start(update, context)  # ফেরত main menu তে যাবে

    elif query.data == "referral":
        await query.message.reply_text("🔗 Your referral link: coming soon...")
    elif query.data == "balance":
        await query.message.reply_text("💰 Your balance: 0 BDT")
    elif query.data == "support":
        await query.message.reply_text("📩 Contact support: @YourSupport")
    elif query.data == "rules":
        await query.message.reply_text("📜 Rules: Withdraw min 100 BDT")
    elif query.data == "tips":
        await query.message.reply_text("💡 Income tips: Work daily to earn more.")

# --- Handle Withdraw Number ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "method" in context.user_data:
        method = context.user_data["method"]
        number = update.message.text
        user = update.message.from_user

        # Admin কে পাঠানো হবে
        msg = f"📥 Withdraw Request\n\n👤 User: {user.first_name}\n🆔 ID: {user.id}\n💳 Method: {method}\n📲 Number: {number}"
        await context.bot.send_message(chat_id=OWNER_ID, text=msg)

        # User কে রেসপন্স
        await update.message.reply_text("✅ Withdraw request sent to admin.\nPlease wait for approval.")

        # ডাটা মুছে ফেলা
        del context.user_data["method"]

# --- Main ---
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
