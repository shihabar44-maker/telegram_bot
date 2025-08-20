from telegram.ext import Updater, CommandHandler

# ---------- Command Functions ----------
def start(update, context):
    update.message.reply_text('⚡ "একটা কমান্ড দিলেই উত্তর তোমার হাতে — এই হলো আমার Telegram Bot!"')

def about(update, context):
    update.message.reply_text('🤖 "আমার নিজের হাতে তৈরি একটি ছোট্ট সহকারী — সবসময় প্রস্তুত তোমার কাজে সাহায্য করার জন্য!"')

def help_command(update, context):
    update.message.reply_text('🛠 "আমি একটা সহকারী Telegram Bot। আমি আপনাকে কীভাবে সাহায্য করতে পারি?"')

def tips(update, context):
    update.message.reply_text('💡 "আমার সম্পর্কে আরো জানতে চাইলে এই লিংকে ক্লিক করুন: https://t.me/sr_sadiya_official"')

# ---------- Main Function ----------
def main():
    TOKEN = "8386188290:AAFA_-VB0LzomH46cXeWEg6OwJP8qNSPzOc"   # এখানে তোমার BotFather থেকে পাওয়া টোকেন বসাবে

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command Handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("tips", tips))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
