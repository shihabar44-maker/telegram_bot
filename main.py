from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# তোমার Bot Token
TOKEN = "8331378652:AAHiopSQE7WLTQzVdifQNdTQ085GXuKXt5I"

# ---------- Telegram Bot ----------
application = Application.builder().token(TOKEN).build()

# ---------- Commands ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💰 My Account", "💬 Support"],
        ["✨ Referral", "💵 Balance"],
        ["⚠️ Rules", "✅ Withdraw"],
        ["🔥 Income Tips"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "👋 হ্যালো! আমি চালু আছি\nনিচের মেনু থেকে যেকোনো একটি বেছে নাও:",
        reply_markup=reply_markup
    )

# ---------- Text Button Handler ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "💰 My Account":
        await update.message.reply_text("🧾 SR SHIHAB 🔴 তোমার অ্যাকাউন্টের তথ্য এখানে!")
    elif text == "💬 Support":
        await update.message.reply_text("📩 সাপোর্ট: SR NIROB @YourSupportID")
    elif text == "💵 Balance":
        await update.message.reply_text("💸 তোমার বর্তমান ব্যালেন্স: 0৳")
    elif text == "✨ Referral":
        await update.message.reply_text("🔗 রেফারেল লিংক: https://t.me/YourBot?start=ref123")
    elif text == "⚠️ Rules":
        await update.message.reply_text("📜 নিয়মাবলী: এখানে নিয়ম লেখা থাকবে।")
    elif text == "✅ Withdraw":
        await update.message.reply_text("✅ ন্যূনতম ১০০৳ হলে উইথড্র করতে পারবে।")
    elif text == "🔥 Income Tips":
        await update.message.reply_text("🎁 ইনকাম করতে বন্ধুদের রেফার করো আর বোনাস পাও!")
    else:
        await update.message.reply_text("❓ আমি এই অপশন চিনতে পারিনি।")

# ---------- Handlers ----------
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

# ---------- Run Polling ----------
if __name__ == "__main__":
    application.run_polling()
