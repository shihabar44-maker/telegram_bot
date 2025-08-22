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

    if text == "💰 My Account 💰":
        await update.message.reply_text("🧾 SR SHIHAB 🔴 তোমার অ্যাকাউন্টের তথ্য এখানে!")
    elif text == "💬 Support":
        await update.message.reply_text("📩 সাপোর্ট: SR NIROB @YourSupportID")
    elif text == "💵 Balance 💵":
        await update.message.reply_text("💸 তোমার বর্তমান ব্যালেন্স: 0৳")
    elif text == "✨ Referral ✨":
        await update.message.reply_text("🔗 রেফারেল লিংক: https://t.me/YourBot?start=ref123")
    elif text == "⚠️ Rules ⚠️":
        await update.message.reply_text("📜 নিয়মাবলী: এখানে নিয়ম লেখা থাকবে।")
    elif text == "✅ Withdraw ✅":
        await update.message.reply_text("Minimum withdraw : 1000 টাকা .

Payment : ( উইথড্র করার 24 ঘন্টার মধ্যে প্রেমেন্ট পেয়ে জাবেন )

🏛 মিনিমাম উইথড্র ব্যালেন্স .
💵 Bkash >1000 টাকা .
💵 Nagad >1000 টাকা.

! আপনার একাউন্টে মিনিমাম 1000 টাকা থাকতে হবে. তাহলে আপনার উইথড্র 100% সাক্সেসফুল হবে.

( প্রতিদিন সবার পেমেন্ট হিস্টরি পেতে বোডের গ্রুপে চোখ রাখুন. ধন্যবাদ. )

⚠️আপনার একাউন্টে বর্তমান ব্যালেন্স রয়েছে 1200 টাকা •")
    elif text == "🔥 Income Tips 🔥":
        await update.message.reply_text("🎁 ইনকাম করতে বন্ধুদের রেফার করো আর বোনাস পাও!")
    else:
        await update.message.reply_text("❓ আমি এই অপশন চিনতে পারিনি।")

# ---------- Handlers ----------
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, button_handler))

# ---------- Run Polling ----------
if __name__ == "__main__":
    application.run_polling()
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton("📱 Share my number", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Hello! Please share your number:", reply_markup=reply_markup)

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    await update.message.reply_text(f"Thanks! I got your number: {contact.phone_number}")

app = Application.builder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
app.run_polling()
