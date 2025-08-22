from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --------------------------
# Replace these with your info
BOT_TOKEN = "8422229356:AAGHAdJCFZNmgNAhx5CchxrM51U53oOc0Ec"   # তোমার BotFather থেকে পাওয়া টোকেন
OWNER_ID = 8028396521           # এখানে তোমার Telegram numeric ID দাও
# --------------------------

# Temporary storage for withdraw requests
withdraw_requests = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["👤 My Account", "💸 Withdraw"],
        ["📎 Referral", "📩 Support"],
        ["📜 Rules", "💡 Income Tips"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🌸 Welcome to your bot! Choose an option:", reply_markup=reply_markup)

# Handle all button clicks
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    # My Account
    if text == "👤 My Account":
        await update.message.reply_text(f"👤 Account Info:\nName: {user.first_name}\nID: {user.id}")

    # Referral
    elif text == "📎 Referral":
        await update.message.reply_text("🔗 Your referral link:\nhttps://t.me/YOUR_BOT?start=" + str(user.id))

    # Support
    elif text == "📩 Support":
        await update.message.reply_text("📬 Contact Support: @yourusername")

    # Rules
    elif text == "📜 Rules":
        await update.message.reply_text("📜 Rules:\n1️⃣ Be honest 🤝\n2️⃣ No spam 🚫\n3️⃣ Respect others 🙏")

    # Income Tips
    elif text == "💡 Income Tips":
        await update.message.reply_text("💡 Income Tips:\n✅ Refer friends 👥\n✅ Stay active ⚡\n✅ Follow updates 🎁")

    # Withdraw
    elif text == "💸 Withdraw":
        keyboard = [["📱 Bkash", "📱 Nagad"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("💰 Select Withdraw Method:", reply_markup=reply_markup)

    # Bkash Withdraw
    elif text == "📱 Bkash":
        context.user_data["method"] = "Bkash"
        await update.message.reply_text("✍ Enter your 📱 Bkash number:")

    # Nagad Withdraw
    elif text == "📱 Nagad":
        context.user_data["method"] = "Nagad"
        await update.message.reply_text("✍ Enter your 📱 Nagad number:")

    # If expecting number
    elif "method" in context.user_data:
        method = context.user_data["method"]
        number = text
        req_id = str(user.id)  # unique request id
        withdraw_requests[req_id] = {"user": user, "method": method, "number": number}

        # Send request to owner
        msg = f"📤 New Withdraw Request\n\n👤 User: {user.first_name} ({user.id})\n💳 Method: {method}\n📱 Number: {number}\n\nReply with YES {req_id} or NO {req_id}"
        await context.bot.send_message(chat_id=OWNER_ID, text=msg)

        await update.message.reply_text("✅ Your request has been sent to admin. Please wait for approval.")
        del context.user_data["method"]  # reset

    else:
        await update.message.reply_text("⚠️ Unknown command.")

# Admin approval (YES / NO)
async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id != OWNER_ID:
        return

    text = update.message.text.split()
    if len(text) == 2:
        command, req_id = text[0].upper(), text[1]

        if req_id in withdraw_requests:
            request = withdraw_requests[req_id]
            target_user = request["user"]

            if command == "YES":
                await context.bot.send_message(chat_id=target_user.id, text="🎉 Your withdraw was successful!")
                await update.message.reply_text(f"✅ Approved withdraw for {target_user.first_name}")

            elif command == "NO":
                await context.bot.send_message(chat_id=target_user.id, text="❌ Your withdraw request was rejected.")
                await update.message.reply_text(f"❌ Rejected withdraw for {target_user.first_name}")

            del withdraw_requests[req_id]

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, admin_response))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
