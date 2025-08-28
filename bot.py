import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# এখানে সরাসরি টোকেন বসান
BOT_TOKEN = "7890244767:AAE4HRfDjhyLce4feEaK_YCgFaJbVHi_2nA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot ঠিকমতো চলছে okay  !")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
