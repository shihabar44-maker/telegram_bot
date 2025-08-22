from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

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
        "✨ Welcome to *SR Media Bot* ✨\n\n"
        "Choose an option below 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# =========================
# My Account Handler
# =========================
async def my_account(update: Update, context: CallbackContext):
    user = update.effective_user

    account_info = f"""
👤 *Your Account Details*:

🆔 *ID:* `{user.id}`
👨‍💻 *Name:* {user.full_name}
📧 *Username:* @{user.username if user.username else "Not set"}
🌐 *Language:* {user.language_code}
    """

    await update.message.reply_text(account_info, parse_mode="Markdown")

# =========================
# Other Buttons Handlers
# =========================
async def referral(update: Update, context: CallbackContext):
    user = update.effective_user
    referral_link = f"https://t.me/YOUR_BOT_USERNAME?start={user.id}"
    await update.message.reply_text(
        f"🔗 *Your Referral Link:*\n\n{referral_link}\n\n"
        "👥 Invite friends & earn rewards! 💎",
        parse_mode="Markdown"
    )

async def withdraw(update: Update, context: CallbackContext):
    await update.message.reply_text("💸 *Withdraw option will be available soon!* ⏳", parse_mode="Markdown")

async def balance(update: Update, context: CallbackContext):
    await update.message.reply_text("💰 *Your Balance:* 0.00 USD 🪙", parse_mode="Markdown")

async def support(update: Update, context: CallbackContext):
    await update.message.reply_text("📩 *Contact Support:* @YourSupportUsername 🛠️", parse_mode="Markdown")

async def rules(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📜 *Rules:*\n\n"
        "1️⃣ Be honest 🤝\n"
        "2️⃣ No spam 🚫\n"
        "3️⃣ Respect others 🙏",
        parse_mode="Markdown"
    )

async def income_tips(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "💡 *Income Tips:*\n\n"
        "✅ Refer friends to earn more 👥\n"
        "✅ Stay active daily ⚡\n"
        "✅ Follow updates for bonuses 🎁",
        parse_mode="Markdown"
    )

# =========================
# Main Function
# =========================
def main():
    TOKEN = "8422229356:AAGHAdJCFZNmgNAhx5CchxrM51U53oOc0Ec"

    app = Application.builder().token(TOKEN).build()

    # Command
    app.add_handler(CommandHandler("start", start))

    # Button Handlers
    app.add_handler(MessageHandler(filters.Regex("^👤 My Account$"), my_account))
    app.add_handler(MessageHandler(filters.Regex("^🔗 Referral$"), referral))
    app.add_handler(MessageHandler(filters.Regex("^💸 Withdraw$"), withdraw))
    app.add_handler(MessageHandler(filters.Regex("^💰 Balance$"), balance))
    app.add_handler(MessageHandler(filters.Regex("^📩 Support$"), support))
    app.add_handler(MessageHandler(filters.Regex("^📜 Rules$"), rules))
    app.add_handler(MessageHandler(filters.Regex("^💡 Income Tips$"), income_tips))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
