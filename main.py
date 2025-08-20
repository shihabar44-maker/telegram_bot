import telebot  

TOKEN = "8386188290:AAFA_-VB0LzomH46cXeWEg6OwJP8qNSPzOc"  

bot = telebot.TeleBot(TOKEN)  

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "হ্যালো 👋 আমি তোমার Telegram Bot 🚀")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "তুমি লিখেছো: " + message.text)

print("Bot is running...")  
bot.infinity_polling()   # <-- bot.polling() এর জায়গায় এটা ভালো কাজ করবে
