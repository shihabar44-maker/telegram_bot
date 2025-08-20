from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8386188290:AAFA_-VB0LzomH46cXeWEg6OwJP8qNSPzOc"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ একটা কমান্ড দিলেই উত্তর তোমার হাতে — এই হলো আমার Telegram Bot!")

# /about command
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("আমার নিজের হাতে তৈরি একটি ছোট্ট সহকারী — সবসময় প্রস্তুত তোমার কাজে সাহায্য করার জন্য!")

# /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("আমি একটা সহকারী Telegram Bot 🧑‍💻 আমি আপনাকে কীভাবে সাহায্য করতে পারি?")

# /tips command
async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("আমার সম্পর্কে আরো জানতে চাইলে 👉 https://t.me/sr_sadiya_official এই লিংকে ক্লিক করুন!")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("tips", tips))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
