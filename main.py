from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Owner ID (Admin এ withdraw request যাবে)
OWNER_ID = 8028396521

# User balances
user_balances = {}

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
    user = update.message.from_user
    if user.id not in user_balances:
        user_balances[user.id] = 50000  # Default balance = ৫০,০০০৳
    await update.message.reply_text(
        "✨ Welcome! Choose an option:",
        reply_markup=reply_markup
    )

# Handle Messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    balance = user_balances.get(user.id, 0)

    if text == "💰 My Account":
        account_text = (
            f"👤 Your Account Details:\n\n"
            f"🆔 ID: {user.id}\n"
            f"👨 Name: {user.first_name}\n"
            f"📛 Username: @{user.username or 'Not set'}\n"
            f"💰 Balance: {balance}৳"
        )
        await update.message.reply_text(account_text, reply_markup=reply_markup)

    elif text == "📢 Referral":
        referral_link = f"https://t.me/YourBot?start={user.id}"
        await update.message.reply_text(
            f"🔗 Your referral link:\n{referral_link}",
            reply_markup=reply_markup
        )

    elif text == "✅ Withdraw":
        if balance < 100:
            await update.message.reply_text(
                "⚠️ মিনিমাম ১০০৳ টাকা হলে withdraw করতে পারবেন!",
                reply_markup=reply_markup
            )
        else:
            withdraw_menu = [
                ["📲 Bkash", "💳 Nagad"],
                ["🔙 Back to Menu"]
            ]
            withdraw_markup = ReplyKeyboardMarkup(withdraw_menu, resize_keyboard=True)
            await update.message.reply_text(
                "💵 Withdraw Method সিলেক্ট করুন:",
                reply_markup=withdraw_markup
            )

    elif text == "📲 Bkash":
        if balance >= 100:
            context.user_data["method"] = "Bkash"
            await update.message.reply_text("📲 আপনার Bkash নাম্বার দিন:")
        else:
            await update.message.reply_text("⚠️ মিনিমাম ১০০৳ টাকা হলে withdraw করতে পারবেন!")

    elif text == "💳 Nagad":
        if balance >= 100:
            context.user_data["method"] = "Nagad"
            await update.message.reply_text("💳 আপনার Nagad নাম্বার দিন:")
        else:
            await update.message.reply_text("⚠️ মিনিমাম ১০০৳ টাকা হলে withdraw করতে পারবেন!")

    elif text == "🔙 Back to Menu":
        await update.message.reply_text("⬅️ Main Menu তে ফিরে গেছেন।", reply_markup=reply_markup)

    elif text == "💵 Balance":
        await update.message.reply_text(
            f"💵 আপনার বর্তমান ব্যালেন্স: {balance}৳",
            reply_markup=reply_markup
        )

    elif text == "💬 Support":
        await update.message.reply_text("📩 সাপোর্ট: @YourSupportID", reply_markup=reply_markup)

    elif text == "⚠️ Rules":
        await update.message.reply_text("⚠️ Rule 1...\n⚠️ Rule 2...", reply_markup=reply_markup)

    elif text == "🔥 Income Tips":
        await update.message.reply_text("🔥 Earn tips will be here.", reply_markup=reply_markup)

    else:
        if "method" in context.user_data:
            method = context.user_data["method"]
            number = text

            # Admin Panel এ Approve/Reject button
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}_{number}_{method}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
                ]
            ])

            msg = (
                f"📥 Withdraw Request\n\n"
                f"👤 User: {user.first_name}\n"
                f"🆔 ID: {user.id}\n"
                f"💳 Method: {method}\n"
                f"📲 Number: {number}\n"
                f"💰 Balance: {balance}৳"
            )
            await context.bot.send_message(chat_id=OWNER_ID, text=msg, reply_markup=buttons)
            await update.message.reply_text("✅ আপনার withdraw request পাঠানো হয়েছে, Admin approve করবে।", reply_markup=reply_markup)
            del context.user_data["method"]

# Callback Handler (Approve/Reject)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    action = data[0]
    user_id = int(data[1])

    if action == "approve":
        number = data[2]
        method = data[3]
        amount = user_balances.get(user_id, 0)

        if amount >= 100:
            user_balances[user_id] -= amount  # সব টাকা কেটে দিলাম, চাইলে fixed amount সেট করতে পারো
            await context.bot.send_message(chat_id=user_id, text=f"✅ আপনার withdraw {amount}৳ Approved হয়েছে!\nMethod: {method}\nNumber: {number}")
            await query.edit_message_text(f"✅ Withdraw Approved for User {user_id}, Amount: {amount}৳")
        else:
            await query.edit_message_text("⚠️ User এর ব্যালেন্স যথেষ্ট নেই।")

    elif action == "reject":
        await context.bot.send_message(chat_id=user_id, text="❌ আপনার withdraw request Rejected হয়েছে।")
        await query.edit_message_text(f"❌ Withdraw Rejected for User {user_id}")

# Main Function
def main():
    app = Application.builder().token("8422229356:AAGHAdJCFZNmgNAhx5CchxrM51U53oOc0Ec").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
