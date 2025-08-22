from collections import defaultdict
from telegram import (
    Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

TOKEN = "8386188290:AAFoWLcvqlk030n1EzHUC2-mJq9vSOSelq0"
OWNER_ID = 8028396521  # এখানে তোমার numeric Telegram ID দাও

# ===== Data store =====
USERS = defaultdict(lambda: {"balance": 0})

# ===== Menus =====
main_menu = ReplyKeyboardMarkup(
    [
        ["🏦 Accounts Sell", "💬 Support Group"],
        ["💰 My Balance", "✅ Withdraw"],
    ],
    resize_keyboard=True
)

sell_menu = ReplyKeyboardMarkup(
    [
        ["📨 Telegram", "📞 WhatsApp"],
        ["⬅️ Back"],
    ],
    resize_keyboard=True
)

back_only = ReplyKeyboardMarkup([["⬅️ Back"]], resize_keyboard=True)

withdraw_menu = ReplyKeyboardMarkup(
    [
        ["📲 Bkash", "💳 Nagad"],
        ["⬅️ Back"],
    ],
    resize_keyboard=True
)

# ===== States =====
CHOOSE_PLATFORM, ASK_NUMBER, ASK_CODE = range(3)
WD_METHOD, WD_NUMBER = range(3, 5)

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    _ = USERS[user.id]  # ensure record exists
    await update.message.reply_text("✨ Welcome! Choose an option:", reply_markup=main_menu)

# ===== Static actions (no conversation) =====
async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bal = USERS[user.id]["balance"]
    await update.message.reply_text(f"💰 আপনার মোট Balance: {bal}৳")

async def support_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬 Support Group: https://t.me/YourSupportGroup")

# ===== Accounts Sell flow =====
async def sell_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("একটি প্ল্যাটফর্ম বাছাই করুন:", reply_markup=sell_menu)
    context.user_data.pop("platform", None)
    context.user_data.pop("acc_number", None)
    return CHOOSE_PLATFORM

async def choose_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📨 Telegram":
        context.user_data["platform"] = "Telegram"
    elif text == "📞 WhatsApp":
        context.user_data["platform"] = "WhatsApp"
    elif text == "⬅️ Back":
        await update.message.reply_text("⬅️ Main Menu", reply_markup=main_menu)
        return ConversationHandler.END
    else:
        await update.message.reply_text("উপরে থেকে একটি অপশন বেছে নিন।", reply_markup=sell_menu)
        return CHOOSE_PLATFORM

    await update.message.reply_text("📲 আপনার Account Number দিন:", reply_markup=back_only)
    return ASK_NUMBER

async def ask_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Back":
        await update.message.reply_text("প্ল্যাটফর্ম বাছাই করুন:", reply_markup=sell_menu)
        return CHOOSE_PLATFORM

    number = update.message.text.strip()
    if len(number) < 5:
        await update.message.reply_text("❌ বৈধ Account Number দিন:", reply_markup=back_only)
        return ASK_NUMBER

    context.user_data["acc_number"] = number
    await update.message.reply_text("🔑 এখন আপনার Account Code দিন:", reply_markup=back_only)
    return ASK_CODE

async def complete_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Back":
        await update.message.reply_text("প্ল্যাটফর্ম বাছাই করুন:", reply_markup=sell_menu)
        return CHOOSE_PLATFORM

    code = update.message.text.strip()
    if not code.isdigit():
        await update.message.reply_text("❌ Code শুধু সংখ্যা হতে হবে!", reply_markup=back_only)
        return ASK_CODE

    user = update.effective_user
    platform = context.user_data.get("platform", "Unknown")
    number = context.user_data.get("acc_number")

    # Add balance +20
    USERS[user.id]["balance"] += 20
    bal = USERS[user.id]["balance"]

    await update.message.reply_text(
        f"✅ Successful!\n"
        f"🗂 Platform: {platform}\n"
        f"📲 Account: {number}\n"
        f"🔑 Code: {code}\n\n"
        f"💰 আপনার নতুন Balance: {bal}৳\n\n"
        f"আরও অ্যাকাউন্ট পাঠাতে চাইলে আবার *Account Number* দিন, "
        f"না হলে '⬅️ Back' চাপুন।",
        reply_markup=back_only
    )
    # 🔁 stay in the same platform for unlimited entries
    return ASK_NUMBER

# ===== Withdraw flow =====
async def withdraw_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bal = USERS[user.id]["balance"]
    if bal < 100:
        await update.message.reply_text("⚠️ মিনিমাম 100৳ হলে withdraw করা যাবে।")
        return ConversationHandler.END

    await update.message.reply_text("Withdraw Method নির্বাচন করুন:", reply_markup=withdraw_menu)
    return WD_METHOD

async def choose_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅️ Back":
        await update.message.reply_text("⬅️ Main Menu", reply_markup=main_menu)
        return ConversationHandler.END

    if text not in ("📲 Bkash", "💳 Nagad"):
        await update.message.reply_text("উপরে থেকে একটি মেথড বেছে নিন:", reply_markup=withdraw_menu)
        return WD_METHOD

    context.user_data["wd_method"] = "Bkash" if text == "📲 Bkash" else "Nagad"
    await update.message.reply_text("আপনার নাম্বার দিন:", reply_markup=back_only)
    return WD_NUMBER

async def take_withdraw_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Back":
        await update.message.reply_text("Withdraw Method নির্বাচন করুন:", reply_markup=withdraw_menu)
        return WD_METHOD

    number = update.message.text.strip()
    user = update.effective_user
    bal = USERS[user.id]["balance"]
    method = context.user_data.get("wd_method", "Unknown")

    # Send request to admin with inline Approve/Reject
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Approve", callback_data=f"wd_approve_{user.id}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"wd_reject_{user.id}")],
        ]
    )
    admin_msg = (
        "📥 Withdraw Request\n\n"
        f"👤 User: {user.first_name} ({user.id})\n"
        f"💰 Balance: {bal}৳ (full)\n"
        f"💳 Method: {method}\n"
        f"📲 Number: {number}"
    )
    await context.bot.send_message(chat_id=OWNER_ID, text=admin_msg, reply_markup=keyboard)
    await update.message.reply_text("✅ আপনার withdraw request অ্যাডমিনের কাছে পাঠানো হয়েছে।", reply_markup=main_menu)
    return ConversationHandler.END

# ===== Admin inline: approve/reject =====
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        action, user_id = query.data.split("_")[1], int(query.data.split("_")[2])
    except Exception:
        await query.edit_message_text("Invalid action.")
        return

    if action == "approve":
        USERS[user_id]["balance"] = 0
        await context.bot.send_message(chat_id=user_id, text="✅ Withdraw APPROVED!\n💰 Balance: 0৳")
        await query.edit_message_text("✅ Approved.")
    elif action == "reject":
        await context.bot.send_message(chat_id=user_id, text="❌ Withdraw REJECTED.")
        await query.edit_message_text("❌ Rejected.")

# ===== Build app =====
def main():
    app = Application.builder().token(TOKEN).build()

    # /start + static
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^💰 My Balance$"), show_balance))
    app.add_handler(MessageHandler(filters.Regex("^💬 Support Group$"), support_group))

    # Accounts Sell conversation
    sell_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🏦 Accounts Sell$"), sell_entry)],
        states={
            CHOOSE_PLATFORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_platform)],
            ASK_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_code)],
            ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_sell)],
        },
        fallbacks=[MessageHandler(filters.Regex("^⬅️ Back$"), sell_entry)],
        name="sell_conv",
        persistent=False,
    )
    app.add_handler(sell_conv)

    # Withdraw conversation
    wd_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^✅ Withdraw$"), withdraw_entry)],
        states={
            WD_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_method)],
            WD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, take_withdraw_number)],
        },
        fallbacks=[MessageHandler(filters.Regex("^⬅️ Back$"), withdraw_entry)],
        name="wd_conv",
        persistent=False,
    )
    app.add_handler(wd_conv)

    # Admin callbacks
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^wd_"))

    app.run_polling()

if __name__ == "__main__":
    main()
