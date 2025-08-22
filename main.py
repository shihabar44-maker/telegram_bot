from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)

# Admin ID
OWNER_ID = 8028396521  # এখানে তোমার Telegram numeric ID বসাও

# User data
user_data = {}

# States for Conversation
ASK_NUMBER, ASK_CODE = range(2)

# Keyboard Layout
main_menu = [
    ["🏦 Accounts Sell", "💬 Support Group"],
    ["💰 My Balance", "✅ Withdraw"]
]
reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)

# Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in user_data:
        user_data[user.id] = {"balance": 0}
    await update.message.reply_text("✨ Welcome! Choose an option:", reply_markup=reply_markup)

# My Balance
async def my_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance = user_data[update.effective_user.id]["balance"]
    await update.message.reply_text(f"💰 আপনার মোট Balance: {balance}৳")

# Step 1: Accounts Sell pressed
async def accounts_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📲 আপনার Account Number দিন:")
    return ASK_NUMBER

# Step 2: User gives number
async def ask_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text
    context.user_data["account_number"] = number
    await update.message.reply_text("🔑 এখন আপনার Account Code দিন:")
    return ASK_CODE

# Step 3: User gives code
async def complete_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    number = context.user_data.get("account_number")

    # Balance add
    user_id = update.effective_user.id
    user_data[user_id]["balance"] += 20
    balance = user_data[user_id]["balance"]

    await update.message.reply_text(
        f"✅ Successful!\n"
        f"📲 Account: {number}\n"
        f"🔑 Code: {code}\n\n"
        f"💰 আপনার নতুন Balance: {balance}৳"
    )
    return ConversationHandler.END

# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Account Sell প্রক্রিয়া বাতিল হয়েছে।", reply_markup=reply_markup)
    return ConversationHandler.END

# Support group
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬 আমাদের Support Group:\n👉 https://t.me/YourSupportGroupLink")

# Withdraw
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    balance = user_data.get(user.id, {}).get("balance", 0)

    if balance < 100:  # মিনিমাম withdraw লিমিট
        await update.message.reply_text("⚠️ মিনিমাম 100৳ হলে withdraw করা যাবে।")
    else:
        # Send request to admin
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]
        ])
        msg = (
            f"📤 Withdraw Request\n\n"
            f"👤 User: {user.first_name}\n"
            f"🆔 ID: {user.id}\n"
            f"💰 Amount: {balance}৳\n"
            f"📱 Method: Bkash/Nagad\n"
            f"Number: Not Provided"
        )
        await context.bot.send_message(chat_id=OWNER_ID, text=msg, reply_markup=keyboard)
        await update.message.reply_text("📩 আপনার withdraw request admin এর কাছে পাঠানো হয়েছে।")

# Admin Callback (Approve/Reject)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    action = data[0]
    user_id = int(data[1])

    if action == "approve":
        if user_id in user_data:
            user_data[user_id]["balance"] = 0
            await context.bot.send_message(chat_id=user_id, text="✅ আপনার withdraw request APPROVED ✅\n💰 Balance: 0৳")
            await query.edit_message_text("✅ Withdraw request approved!")
    elif action == "reject":
        await context.bot.send_message(chat_id=user_id, text="❌ আপনার withdraw request REJECTED ❌")
        await query.edit_message_text("❌ Withdraw request rejected!")

# Main function
def main():
    app = Application.builder().token("8386188290:AAFoWLcvqlk030n1EzHUC2-mJq9vSOSelq0").build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🏦 Accounts Sell$"), accounts_sell)],
        states={
            ASK_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_code)],
            ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_sell)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("^💰 My Balance$"), my_balance))
    app.add_handler(MessageHandler(filters.Regex("^💬 Support Group$"), support))
    app.add_handler(MessageHandler(filters.Regex("^✅ Withdraw$"), withdraw))
    app.add_handler(CallbackQueryHandler(button_callback))

    app.run_polling()

if __name__ == "__main__":
    main()
