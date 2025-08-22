from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# =========================
# আপনার Owner ID বসান
# =========================
OWNER_ID = 8028396521  # এখানে নিজের Telegram numeric ID বসান

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
        "✨ Welcome to *Love IE Fake Bot* ✨\n\n"
        "Choose an option below 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# =========================
# My Account
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
# Referral
# =========================
async def referral(update: Update, context: CallbackContext):
    user = update.effective_user
    referral_link = f"https://t.me/{context.bot.username}?start={user.id}"
    await update.message.reply_text(
        f"🔗 *Your Referral Link:*\n\n{referral_link}\n\n"
        "👥 Invite friends & earn rewards! 💎",
        parse_mode="Markdown"
    )

# =========================
# Withdraw
# =========================
async def withdraw(update: Update, context: CallbackContext):
    keyboard = [
        [KeyboardButton("📲 Bkash"), KeyboardButton("💳 Nagad")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("💸 Choose your withdraw method 👇", reply_markup=reply_markup)

async def withdraw_method(update: Update, context: CallbackContext):
    user = update.effective_user
    method = update.message.text

    if method == "📲 Bkash":
        msg = f"📲 User {user.full_name} ({user.id}) selected *Bkash*.\nPlease ask them for their number."
    elif method == "💳 Nagad":
        msg = f"💳 User {user.full_name} ({user.id}) selected *Nagad*.\nPlease ask them for their number."
    else:
        return

    # Owner কে মেসেজ পাঠানো
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"⚠️ Withdraw Request:\n\n{msg}\n\nApprove? Reply with /approve {user.id} or /reject {user.id}"
    )

    await update.message.reply_text("✅ Withdraw request sent to admin. Please wait for approval.")

# =========================
# Admin Commands
# =========================
async def approve(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /approve <user_id>")
    
    user_id = int(context.args[0])
    await context.bot.send_message(user_id, "🎉 Your withdraw has been *Approved* ✅")
    await update.message.reply_text(f"👍 Approved withdraw for user {user_id}")

async def reject(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        return
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /reject <user_id>")
    
    user_id = int(context.args[0])
    await context.bot.send_message(user_id, "❌ Your withdraw request has been *Rejected*")
    await update.message.reply_text(f"👎 Rejected withdraw for user {user_id}")

# =========================
# Balance
# =========================
async def balance(update: Update, context: CallbackContext):
    await update.message.reply_text("💰 *Your Balance:* 0.00 USD 🪙", parse_mode="Markdown")

# =========================
# Support
# =========================
async def support(update: Update, context: CallbackContext):
    await update.message.reply_text("📩 *Contact Support:* @your_support_id 🛠️", parse_mode="Markdown")

# =========================
# Rules
# =========================
async def rules(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📜 *Rules:*\n\n"
        "1️⃣ Be honest 🤝\n"
        "2️⃣ No spam 🚫\n"
        "3️⃣ Respect others 🙏",
        parse_mode="Markdown"
    )

# =========================
# Income Tips
# =========================
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
    app.add_handler(CommandHandler("approve", approve))
    app.add_handler(CommandHandler("reject", reject))

    # Button Handlers
    app.add_handler(MessageHandler(filters.Regex("^👤 My Account$"), my_account))
    app.add_handler(MessageHandler(filters.Regex("^🔗 Referral$"), referral))
    app.add_handler(MessageHandler(filters.Regex("^💸 Withdraw$"), withdraw))
    app.add_handler(MessageHandler(filters.Regex("^(📲 Bkash|💳 Nagad)$"), withdraw_method))
    app.add_handler(MessageHandler(filters.Regex("^💰 Balance$"), balance))
    app.add_handler(MessageHandler(filters.Regex("^📩 Support$"), support))
    app.add_handler(MessageHandler(filters.Regex("^📜 Rules$"), rules))
    app.add_handler(MessageHandler(filters.Regex("^💡 Income Tips$"), income_tips))

    print("🚀 Bot is running with polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
