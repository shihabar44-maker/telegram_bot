from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Steps for Withdraw
SELECT_METHOD, ENTER_NUMBER, CONFIRM = range(3)

OWNER_ID = 8028396521  # 👉 এখানে তোমার নিজের Telegram ID বসাও (যেখানে withdraw request যাবে)

# =========================
# Start Command
# =========================
async def start(update: Update, context: CallbackContext):
    keyboard = [
        ["👤 My Account", "🔗 Referral"],
        ["💸 Withdraw", "💰 Balance"],
        ["📩 Support", "📜 Rules"],
        ["💡 Income Tips"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "✨ Welcome to *Love Ie Fake😥* ✨\n\n"
        "Choose an option below 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# =========================
# Withdraw Start
# =========================
async def withdraw(update: Update, context: CallbackContext):
    keyboard = [["📲 Bkash", "💳 Nagad"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("💸 Select Withdraw Method:", reply_markup=reply_markup)
    return SELECT_METHOD

# =========================
# Select Method
# =========================
async def select_method(update: Update, context: CallbackContext):
    method = update.message.text
    context.user_data["method"] = method
    await update.message.reply_text(f"✍️ Enter your {method} number:")
    return ENTER_NUMBER

# =========================
# Enter Number
# =========================
async def enter_number(update: Update, context: CallbackContext):
    number = update.message.text
    method = context.user_data["method"]
    user = update.effective_user

    # Save info
    context.user_data["number"] = number

    # Send request to OWNER
    msg = (
        f"📥 *New Withdraw Request*\n\n"
        f"👤 User: {user.full_name} (`{user.id}`)\n"
        f"💳 Method: {method}\n"
        f"📲 Number: {number}\n\n"
        f"Reply 'YES {user.id}' to approve or 'NO {user.id}' to reject."
    )
    await context.bot.send_message(chat_id=OWNER_ID, text=msg, parse_mode="Markdown")

    await update.message.reply_text("✅ Your request has been sent to admin. Please wait for approval.")
    return ConversationHandler.END

# =========================
# Owner Approval
# =========================
async def owner_reply(update: Update, context: CallbackContext):
    text = update.message.text.split()
    if len(text) == 2 and text[0].upper() in ["YES", "NO"]:
        action, user_id = text[0].upper(), text[1]
        try:
            user_id = int(user_id)
            if action == "YES":
                await context.bot.send_message(chat_id=user_id, text="🎉 Your Withdraw is Successful ✅")
                await update.message.reply_text("👍 Approved successfully.")
            else:
                await context.bot.send_message(chat_id=user_id, text="❌ Your Withdraw was Rejected.")
                await update.message.reply_text("👎 Rejected successfully.")
        except:
            await update.message.reply_text("⚠️ Invalid User ID format.")
    else:
        await update.message.reply_text("⚠️ Use 'YES <id>' or 'NO <id>'")

# =========================
# Main Function
# =========================
def main():
    TOKEN = "8422229356:AAGHAdJCFZNmgNAhx5CchxrM51U53oOc0Ec"

    app = Application.builder().token(TOKEN).build()

    # Withdraw Conversation
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💸 Withdraw$"), withdraw)],
        states={
            SELECT_METHOD: [MessageHandler(filters.Regex("^(📲 Bkash|💳 Nagad)$"), select_method)],
            ENTER_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_number)],
        },
        fallbacks=[],
    )
    app.add_handler(conv_handler)

    # Owner approval
    app.add_handler(MessageHandler(filters.TEXT & filters.User(OWNER_ID), owner_reply))

    # Start command
    app.add_handler(CommandHandler("start", start))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
