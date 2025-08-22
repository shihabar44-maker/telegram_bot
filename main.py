from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Owner/Admin ID
OWNER_ID = 8028396521  # এখানে তোমার numeric Telegram ID বসাও

# User data dictionary
user_data = {}  # প্রতিটি ইউজারের balance এখানে save হবে

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
    user = update.effective_user

    # যদি নতুন ইউজার হয়, তাহলে ৫০,০০০ টাকা balance দিবে
    if user.id not in user_data:
        user_data[user.id] = {"balance": 50000}

    await update.message.reply_text(
        "✨ Welcome! Choose an option:",
        reply_markup=reply_markup
    )

# Handle menu clicks
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    # My Account
    if text == "💰 My Account":
        balance = user_data.get(user.id, {}).get("balance", 0)
        msg = (
            f"🧑 Your Account Details:\n\n"
            f"🆔 ID: {user.id}\n"
            f"👨 Name: {user.first_name}\n"
            f"📛 Username: @{user.username or 'Not set'}\n"
            f"💰 Balance: {balance}৳"
        )
        await update.message.reply_text(msg)

    # Balance
    elif text == "💵 Balance":
        balance = user_data.get(user.id, {}).get("balance", 0)
        await update.message.reply_text(f"💰 তোমার বর্তমান ব্যালেন্স: {balance}৳")

    # Withdraw
    elif text == "✅ Withdraw":
        balance = user_data.get(user.id, {}).get("balance", 0)
        if balance < 100:
            await update.message.reply_text("⚠️ মিনিমাম ১০০৳ টাকা হলে withdraw করতে পারবেন!")
        else:
            # Owner কে withdraw request পাঠানো হবে
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}")],
                [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]
            ])
            msg = (
                f"📤 Withdraw Request\n\n"
                f"👤 User: {user.first_name}\n"
                f"🆔 ID: {user.id}\n"
                f"💰 Balance: {balance}৳\n"
                f"📱 Method: Bkash/Nagad\n"
                f"Number: Not Provided"
            )
            await context.bot.send_message(chat_id=OWNER_ID, text=msg, reply_markup=keyboard)
            await update.message.reply_text("📩 তোমার withdraw request admin এর কাছে পাঠানো হয়েছে।")

    # Support
    elif text == "💬 Support":
        await update.message.reply_text("📩 সাপোর্টের জন্য যোগাযোগ করুন: @love_ie_fake")

    # Rules
    elif text == "⚠️ Rules":
        await update.message.reply_text("⚠️ মিনিমাম withdraw 100৳\n⚠️ একাধিক fake request করলে ব্যান করা হবে।")

    # Income Tips
    elif text == "🔥 Income Tips":
        await update.message.reply_text("🔥 বেশি referral আনলে বেশি income হবে!\n🔥 প্রতিদিন Active থাকলে Bonus পাবেন।")

# Admin Callback (Approve/Reject)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    action = data[0]
    user_id = int(data[1])

    if action == "approve":
        if user_id in user_data:
            user_data[user_id]["balance"] = 0  # balance শূন্য করে দিচ্ছে
            await context.bot.send_message(chat_id=user_id, text="✅ তোমার withdraw request APPROVED ✅\n💰 Balance: 0৳")
            await query.edit_message_text("✅ Withdraw request approved!")
    elif action == "reject":
        await context.bot.send_message(chat_id=user_id, text="❌ তোমার withdraw request REJECTED ❌")
        await query.edit_message_text("❌ Withdraw request rejected!")

# Main Function
def main():
    app = Application.builder().token("8422229356:AAGHAdJCFZNmgNAhx5CchxrM51U53oOc0Ec").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))

    app.run_polling()

if __name__ == "__main__":
    main()
