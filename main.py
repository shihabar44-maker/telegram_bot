from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8386188290:AAFA_-VB0LzomH46cXeWEg6OwJP8qNSPzOc"

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("হ্যালো 👋 আমি চালু আছি!")

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔹 Available Commands:\n"
        "/start - Bot চালু করো\n"
        "/help - সাহায্য নাও\n"
        "/about - Bot সম্পর্কে জানো\n"
        "/ping - Bot ঠিক আছে কিনা দেখো"
    )

# /about
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 আমি একটা Telegram Bot, Python দিয়ে বানানো!")

# /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot চলছে!")

def main():
    app = Application.builder().token(TOKEN).build()

    # শুধু কমান্ডগুলো কাজ করবে
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("ping", ping))

    app.run_polling()

if __name__ == "__main__":
    main()
