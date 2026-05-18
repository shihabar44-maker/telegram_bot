import telebot
import google.generativeai as genai
from flask import Flask
from threading import Thread
import os

# ১. Render-এর পোর্ট এরর ফিক্স করার জন্য একটি ছোট ডামি ওয়েব সার্ভার
app = Flask('')

@app.route('/')
def home():
    return "🤖 Bot is running 24/7!"

def run():
    # Render সাধারণত 10000 পোর্টে রান করতে বলে, না পেলে 8080 নেবে
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ২. বটের মূল কনফিগারেশন
BOT_TOKEN = "8994577792:AAGCJ0tvIbTud9P125XUxPugaz6PfRFgxHo"
GEMINI_API_KEY = "AIzaSyAZUZfNfUnxD5mRkd7ODfIiR75KBEbt58s"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 আমি সচল আছি! আমাকে যেকোনো প্রশ্ন করতে পারেন।")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        error_msg = f"❌ এআই সার্ভার এরর:\n`{str(e)}`"
        bot.reply_to(message, error_msg, parse_mode="Markdown")

if __name__ == "__main__":
    # ডামি সার্ভার চালু করা যেন Render পোর্ট খুঁজে পায়
    keep_alive()
    print("🤖 বট সফলভাবে চালু হয়েছে এবং মেসেজের জন্য অপেক্ষা করছে...")
    
    # কনফ্লিক্ট এড়াতে পুরোনো কোনো পেন্ডিং রিকোয়েস্ট থাকলে তা ডিলিট করা
    bot.remove_webhook()
    
    # মূল পোলিং শুরু
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
