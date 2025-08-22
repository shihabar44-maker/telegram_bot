from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8422229356:AAGHAdJCFZNmgNAhx5CchxrM51U53oOc0Ec"
OWNER_ID = 8028396521  # এখানে তোমার Telegram ID বসাও

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👤 My Account", callback_data="account")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("💡 Income Tips", callback_data="tips")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome to the bot! Choose option 👇", reply_markup=reply_markup)

# Handle button clicks
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "account":
        user = query.from_user
        text = f"👤 Your Account Details:\n\n🆔 ID: {user.id}\n👨 Name: {user.first_name}\n💻 Username: @{user.username if user.username else 'Not set'}"
        await query.message.reply_text(text)

    elif query.data == "withdraw":
        keyboard = [
            [InlineKeyboardButton("📱 Bkash", callback_data="bkash")],
            [InlineKeyboardButton("💳 Nagad", callback_data="nagad")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("💸 Choose your withdraw method 👇", reply_markup=reply_markup)

    elif query.data == "bkash":
        await query.message.reply_text("📱 Please enter your Bkash number:", reply_markup=ForceReply())
        context.user_data["method"] = "Bkash"

    elif query.data == "nagad":
        await query.message.reply_text("💳 Please enter your Nagad number:", reply_markup=ForceReply())
        context.user_data["method"] = "Nagad"

# Handle user input (number)
async def handle_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    method = context.user_data.get("method", "Unknown")
    number = update.message.text

    # Send to Admin
    msg = f"🔔 Withdraw Request!\n\n🆔 ID: {user.id}\n👨 Name: {user.first_name}\n💳 Method: {method}\n📱 Number: {number}"
    await context.bot.send_message(chat_id=OWNER_ID, text=msg)

    # Confirm to user
    await update.message.reply_text("✅ Withdraw request sent to admin.\nPlease wait for approval.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number))

    app.run_polling()

if __name__ == "__main__":
    main()
