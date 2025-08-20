import telebot
from flask import Flask
import threading

TOKEN = "8386188290:AAFA_-VB0LzomH46cXeWEg6OwJP8qNSPzOc"
bot = telebot.TeleBot(TOKEN)

# === Telegram Bot Handlers ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "হ্যালো 👋 আমি চালু আছি!")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, "তুমি লিখেছো: " + message.text)

# === Flask Server (for Render) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running on Render!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

# === Start Both Flask + Bot ===
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("Bot is running...")
    bot.infinity_polling()
