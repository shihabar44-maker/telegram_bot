from collections import defaultdict
import re
import logging
from telegram import (
    Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes, filters
)

# ===== Logging Setup =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8386188290:AAFoWLcvqlk030n1EzHUC2-mJq9vSOSelq0"
OWNER_ID = 8028396521   # তোমার Numeric Telegram ID এখানে দাও

# ===== Data Store =====
USERS = defaultdict(lambda: {"balance": 0})
PENDING = {}  # user_id -> {platform, number, code}

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

# ===== Phone Validation =====
def is_valid_phone(number: str) -> bool:
    pattern = r'^\+\d{7,15}$'
    return re.match(pattern, number) is not None

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info("User %s (%s) started the bot.", user.first_name, user.id)
    USERS[user.id]
    await update.message.reply_text("✨ Welcome! Choose an option:", reply_markup=main_menu)

# ===== Static =====
async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bal = USERS[user.id]["balance"]
    await update.message.reply_text(f"💰 Balance: {bal}৳")

async def support_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬 Support Group: https://t.me/love_ie_fake এডমিন এর সাথে যোগাযোগ করতে Send Message এ ক্লিক করুন!")

# ===== Accounts Sell Flow =====
async def sell_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("একটি প্ল্যাটফর্ম বেছে নিন:", reply_markup=sell_menu)
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
        await update.message.reply_text("একটি অপশন বেছে নিন:", reply_markup=sell_menu)
        return CHOOSE_PLATFORM

    await update.message.reply_text("📲 আপনার Account Number দিন:", reply_markup=back_only)
    return ASK_NUMBER

async def ask_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Back":
        await update.message.reply_text("একটি প্ল্যাটফর্ম বেছে নিন:", reply_markup=sell_menu)
        return CHOOSE_PLATFORM

    number = update.message.text.strip()
    if len(number) < 5:
        await update.message.reply_text("❌ বৈধ Account Number দিন:", reply_markup=back_only)
        return ASK_NUMBER

    context.user_data["acc_number"] = number
    await update.message.reply_text("Send OTP:", reply_markup=back_only)
    return ASK_CODE

async def complete_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Back":
        return await sell_entry(update, context)

    code = update.message.text.strip()
    if not code.isdigit():
        await update.message.reply_text("❌ Code শুধু সংখ্যা হতে হবে!", reply_markup=back_only)
        return ASK_CODE

    platform = context.user_data.get("platform")
    number = context.user_data.get("acc_number")
    user = update.effective_user

    # Send request to admin
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Approve", callback_data=f"sell_approve_{user.id}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"sell_reject_{user.id}")]
        ]
    )
    msg = (
        "🛒 Sell Request\n\n"
        f"👤 User: {user.first_name} ({user.id})\n"
        f"🗂 Platform: {platform}\n"
        f"📲 Account: {number}\n"
        f"🔑 Code: {code}"
    )
    await context.bot.send_message(chat_id=OWNER_ID, text=msg, reply_markup=keyboard)

    await update.message.reply_text(
        "🔃 Processing your request...।\n\n👉 নতুন Account দিতে চাইলে আবার নাম্বার লিখুন অথবা ⬅️ Back চাপুন।",
        reply_markup=back_only
    )

    # Save pending
    PENDING[user.id] = {
        "platform": platform,
        "number": number,
        "code": code,
    }
    return ASK_NUMBER

# ===== Withdraw Flow =====
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
        return await start(update, context)
    if text not in ("📲 Bkash", "💳 Nagad"):
        await update.message.reply_text("উপরে থেকে একটি মেথড বেছে নিন:", reply_markup=withdraw_menu)
        return WD_METHOD

    context.user_data["wd_method"] = text.replace("📲 ", "").replace("💳 ", "")
    await update.message.reply_text("আপনার নাম্বার দিন (+880... format):", reply_markup=back_only)
    return WD_NUMBER

async def take_withdraw_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    user = update.effective_user

    if number == "⬅️ Back":
        return await withdraw_entry(update, context)
    if not is_valid_phone(number):
        await update.message.reply_text("❌ সঠিক নাম্বার দিন! Format: +CountryCodeXXXXXXXX")
        return WD_NUMBER

    bal = USERS[user.id]["balance"]
    method = context.user_data.get("wd_method")

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Approve", callback_data=f"wd_approve_{user.id}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"wd_reject_{user.id}")]
        ]
    )
    msg = (
        "📥 Withdraw Request\n\n"
        f"👤 User: {user.first_name} ({user.id})\n"
        f"💰 Balance: {bal}৳\n"
        f"💳 Method: {method}\n"
        f"📲 Number: {number}"
    )
    await context.bot.send_message(chat_id=OWNER_ID, text=msg, reply_markup=keyboard)
    await update.message.reply_text("🔃 withdraw request Processing...", reply_markup=main_menu)
    return ConversationHandler.END

# ===== Admin Callbacks =====
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    category, action, user_id = data[0], data[1], int(data[2])

    if category == "sell":
        pending = PENDING.get(user_id)
        if not pending:
            await query.edit_message_text("⚠️ Request expired or not found.")
            return

        platform, number, code = pending["platform"], pending["number"], pending["code"]

        if action == "approve":
            # user notify
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"✅ Account Sell Successful!\n\n"
                    f"🗂 Platform: {platform}\n"
                    f"📲 Account: {number}\n"
                    f"🔑 Code: {code}\n\n"
                    f"💰 Claim করতে নিচের বাটন চাপুন:"
                ),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🎁 Claim 20৳", callback_data=f"claim_{user_id}")]]
                )
            )
            await query.edit_message_text("✅ Approved & User Notified.")
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"❌ Account Sell Unsuccessful !\n\n"
                    f"🗂 Platform: {platform}\n"
                    f"📲 Account: {number}\n"
                    f"🔑 Code: {code}\n\n"
                    f"⚠️ আবার চেষ্টা করুন অথবা Support Group এ যোগাযোগ করুন।"
                )
            )
            await query.edit_message_text("❌ Rejected & User Notified.")

        del PENDING[user_id]

    elif category == "wd":
        if action == "approve":
            USERS[user_id]["balance"] = 0
            await context.bot.send_message(chat_id=user_id, text="✅ Withdraw Successful!\n💰 Balance: 0৳")
            await query.edit_message_text("✅ Withdraw Approved & User Notified.")
        else:
            await context.bot.send_message(chat_id=user_id, text="❌ Withdraw Rejected.")
            await query.edit_message_text("❌ Withdraw Rejected & User Notified.")

# ===== Claim Callback =====
async def claim_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, user_id = query.data.split("_")
    user_id = int(user_id)

    # একবার Claim করলে আবার হবে না
    if query.message.reply_markup is None:
        await query.edit_message_text("⚠️ Already Claimed.")
        return

    USERS[user_id]["balance"] += 20
    bal = USERS[user_id]["balance"]

    await query.edit_message_text("🎁 20৳ Claimed. ✅ (Already added to your balance)")
    await context.bot.send_message(
        chat_id=user_id,
        text=f"🎁 20৳ Claim সফল হয়েছে!\n💰 নতুন Balance: {bal}৳"
    )

# ===== Build app =====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^💰 My Balance$"), show_balance))
    app.add_handler(MessageHandler(filters.Regex("^💬 Support Group$"), support_group))

    # Sell Flow
    sell_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🏦 Accounts Sell$"), sell_entry)],
        states={
            CHOOSE_PLATFORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_platform)],
            ASK_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_code)],
            ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_sell)],
        },
        fallbacks=[MessageHandler(filters.Regex("^⬅️ Back$"), sell_entry)],
    )
    app.add_handler(sell_conv)

    # Withdraw Flow
    wd_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^✅ Withdraw$"), withdraw_entry)],
        states={
            WD_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_method)],
            WD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, take_withdraw_number)],
        },
        fallbacks=[MessageHandler(filters.Regex("^⬅️ Back$"), withdraw_entry)],
    )
    app.add_handler(wd_conv)

    # Admin Approve/Reject
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(sell|wd)_"))

    # Claim আলাদা
    app.add_handler(CallbackQueryHandler(claim_callback, pattern="^claim_"))

    logger.info("Bot started polling...")
    app.run_polling()

if __name__ == "__main__":
    main() 
