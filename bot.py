import telebot
import google.generativeai as genai

# তোমার টোকেন এবং এপিআই কী এখানে বসাও
BOT_TOKEN = "8994577792:AAGCJ0tvIbTud9P125XUxPugaz6PfRFgxHo"
GEMINI_API_KEY = "AIzaSyAZUZfNfUnxD5mRkd7ODfIiR75KBEbt58s"

# জেমিনি এআই কনফিগারেশন (নতুন নিয়ম)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 আমি সচল আছি! আমাকে যেকোনো প্রশ্ন করতে পারেন।")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # জেমিনি থেকে উত্তর নেওয়া (নতুন নিয়ম)
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "❌ দুঃখিত, উত্তরটি তৈরি করার সময় এআই সার্ভারে একটি সমস্যা হয়েছে।")

print("🤖 বট সফলভাবে চালু হয়েছে এবং মেসেজের জন্য অপেক্ষা করছে...")
bot.infinity_polling(timeout=10, long_polling_timeout=5)
