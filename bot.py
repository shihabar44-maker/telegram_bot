import os
import requests
import telebot
import google.generativeai as genai

#--- [কনফিগারেশন] ---
# @BotFather থেকে পাওয়া টোকেনটি এখানে বসাও
BOT_TOKEN = "8994577792:AAG00RCLPOBvPATFArRCekhXPouLJ5NI3Sw"

# গুগল এআই স্টুডিও থেকে পাওয়া এপিআই কী-টি এখানে বসাও
GEMINI_API_KEY = "AIzaSyAZUZfNfUnxD5mRkd7ODfIiR75KBEbt58s"
#---------------------

# টেলিগ্রাম এবং জেমিনি এআই সেটআপ
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

print("🤖 বট সফলভাবে চালু হয়েছে এবং মেসেজের জন্য অপেক্ষা করছে...")

# /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 স্বাগতম! আমি একটি অল-ইন-ওয়ান এআই বট।\n\n"
        "💬 **যেকোনো প্রশ্নের উত্তর পেতে:** আমাকে সরাসরি যেকোনো মেসেজ বা প্রশ্ন লিখে পাঠাও।\n\n"
        "🎨 **এআই ছবি তৈরি করতে:** মেসেজের শুরুতে `/image` লিখে তারপর কেমন ছবি চাও তা ইংরেজিতে বর্ণনা করো।\n"
        "যেমন: `/image a futuristic gaming room with dark red and neon lighting`"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# ছবি জেনারেট করার হ্যান্ডলার (/image কমান্ড)
@bot.message_handler(commands=['image'])
def generate_image(message):
    # কমান্ডের পরের অংশ (প্রম্পট) আলাদা করা
    prompt = message.text[7:].strip()
    
    if not prompt:
        bot.reply_to(message, "⚠️ দয়া করে `/image` লেখার পর একটি প্রম্পট দিন। যেমন: `/image a neon cyber cat`")
        return
    
    # ইউজারকে জানানো হচ্ছে যে কাজ চলছে
    status_msg = bot.reply_to(message, "⏳ আপনার ছবিটি তৈরি হচ্ছে, একটু অপেক্ষা করুন...")
    
    try:
        # Pollinations AI এর ফ্রি ইমেজ জেনারেশন লিংক তৈরি (স্পেসগুলো %20 দিয়ে রিপ্লেস করা হয়েছে)
        encoded_prompt = prompt.replace(" ", "%20")
        image_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1080&height=1080&nologo=true"
        
        # ছবি ডাউনলোড করে টেলিগ্রামে পাঠানো
        response = requests.get(image_url, timeout=30)
        if response.status_code == 200:
            bot.delete_message(message.chat.id, status_msg.message_id) # 'অপেক্ষা করুন' মেসেজটি ডিলিট করা
            bot.send_photo(message.chat.id, response.content, caption=f"🎨 **আপনার প্রম্পট:** {prompt}", parse_mode='Markdown')
        else:
            bot.edit_message_text("❌ দুঃখিত, এই মুহূর্তে ইমেজ সার্ভার সাড়া দিচ্ছে না।", message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ ছবি তৈরি করার সময় একটি সমস্যা হয়েছে।", message.chat.id, status_msg.message_id)
        print(f"Error generating image: {e}")

# সাধারণ টেক্সট মেসেজ হ্যান্ডলার (Gemini AI এর মাধ্যমে উত্তর)
@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    user_query = message.text
    
    # টাইপিং অ্যানিমেশন দেখানো (যাতে ইউজার বোঝে বট কাজ করছে)
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Gemini AI থেকে উত্তর নেওয়া
        response = model.generate_content(user_query)
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, "❌ দুঃখিত, উত্তরটি তৈরি করার সময় এআই সার্ভারে একটি সমস্যা হয়েছে।")
        print(f"Error with Gemini API: {e}")

# বটটিকে সবসময় চালু রাখার জন্য
bot.infinity_polling()
