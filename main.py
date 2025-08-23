import logging
import re
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

API_TOKEN = "8386188290:AAFoWLcvqlk030n1EzHUC2-mJq9vSOSelq0"   # <-- তোমার BotFather থেকে পাওয়া token
ADMIN_ID = 8028396521          # <-- তোমার Telegram ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Users data store (temporary - DB connect করা যাবে পরে)
users = {}

# --- States ---
class SellAccount(StatesGroup):
    waiting_for_platform = State()
    waiting_for_number = State()
    waiting_for_code = State()

class Withdraw(StatesGroup):
    waiting_for_number = State()
    waiting_for_amount = State()


# --- Start ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"balance": 0}

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🏦 Accounts Sell", "💬 Support Group")
    keyboard.add("💰 My Balance", "✅ Withdraw")
    await message.answer("👋 Welcome! নিচে থেকে একটি অপশন বেছে নিন:", reply_markup=keyboard)


# --- Accounts Sell ---
@dp.message_handler(lambda m: m.text == "🏦 Accounts Sell")
async def accounts_sell(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📲 Telegram", "📞 WhatsApp")
    await message.answer("একটি প্ল্যাটফর্ম বেছে নিন:", reply_markup=keyboard)
    await SellAccount.waiting_for_platform.set()


@dp.message_handler(state=SellAccount.waiting_for_platform)
async def process_platform(message: types.Message, state: FSMContext):
    if message.text not in ["📲 Telegram", "📞 WhatsApp"]:
        await message.answer("❌ সঠিক প্ল্যাটফর্ম বেছে নিন।")
        return

    await state.update_data(platform=message.text)
    await message.answer("📱 আপনার Account Number দিন (country code সহ):")
    await SellAccount.waiting_for_number.set()


@dp.message_handler(state=SellAccount.waiting_for_number)
async def process_number(message: types.Message, state: FSMContext):
    number = message.text.strip()
    if not re.match(r"^\+\d{6,15}$", number):
        await message.answer("❌ সঠিক নাম্বার দিন (country code সহ)। উদাহরণ: +88017XXXXXXX")
        return

    await state.update_data(number=number)
    await message.answer("🔑 আপনার Account Code দিন:")
    await SellAccount.waiting_for_code.set()


@dp.message_handler(state=SellAccount.waiting_for_code)
async def process_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    platform = data["platform"]
    number = data["number"]

    users[message.from_user.id].update({
        "platform": platform,
        "number": number,
        "code": code
    })

    # Send request to admin
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{message.from_user.id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{message.from_user.id}")
    )
    await bot.send_message(
        ADMIN_ID,
        f"📢 নতুন Accounts Sell Request:\n\n"
        f"👤 User: {message.from_user.id}\n"
        f"📲 Platform: {platform}\n"
        f"📱 Number: {number}\n"
        f"🔑 Code: {code}",
        reply_markup=keyboard
    )

    await message.answer("✅ আপনার রিকোয়েস্ট Admin এর কাছে পাঠানো হয়েছে।")
    await state.finish()


# --- Admin approve/reject ---
@dp.callback_query_handler(lambda c: c.data.startswith("approve_") or c.data.startswith("reject_"))
async def process_admin_action(callback: types.CallbackQuery):
    action, user_id = callback.data.split("_")
    user_id = int(user_id)

    if action == "approve":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🎁 Claim 20৳", callback_data=f"claim_{user_id}"))
        await bot.send_message(
            user_id,
            f"✅ আপনার Account Sell request Approved!\n\n"
            f"📲 Platform: {users[user_id]['platform']}\n"
            f"📱 Account: {users[user_id]['number']}\n"
            f"🔑 Code: {users[user_id]['code']}\n\n"
            f"💰 Claim করতে নিচের বাটন চাপুন:",
            reply_markup=keyboard
        )
    else:
        await bot.send_message(user_id, "❌ আপনার Account Sell request Rejected.")

    await callback.answer("Done!")


# --- Claim balance ---
@dp.callback_query_handler(lambda c: c.data.startswith("claim_"))
async def claim_balance(callback: types.CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    users[user_id]["balance"] += 20
    await callback.answer("✅ Successfully claimed 20৳!", show_alert=True)
    await bot.send_message(user_id, f"🎉 আপনার একাউন্টে এখন মোট {users[user_id]['balance']}৳ আছে।")


# --- My Balance ---
@dp.message_handler(lambda m: m.text == "💰 My Balance")
async def my_balance(message: types.Message):
    balance = users[message.from_user.id]["balance"]
    await message.answer(f"💳 আপনার Balance: {balance}৳")


# --- Withdraw ---
@dp.message_handler(lambda m: m.text == "✅ Withdraw")
async def withdraw(message: types.Message):
    await message.answer("📱 আপনার Withdraw Number দিন (country code সহ):")
    await Withdraw.waiting_for_number.set()


@dp.message_handler(state=Withdraw.waiting_for_number)
async def withdraw_number(message: types.Message, state: FSMContext):
    number = message.text.strip()
    if not re.match(r"^\+\d{6,15}$", number):
        await message.answer("❌ সঠিক নাম্বার দিন (country code সহ)। উদাহরণ: +88017XXXXXXX")
        return

    await state.update_data(number=number)
    await message.answer("💵 আপনার Withdraw Amount দিন:")
    await Withdraw.waiting_for_amount.set()


@dp.message_handler(state=Withdraw.waiting_for_amount)
async def withdraw_amount(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ শুধুমাত্র সংখ্যায় Amount দিন।")
        return

    amount = int(message.text)
    user_id = message.from_user.id

    if amount > users[user_id]["balance"]:
        await message.answer("❌ আপনার কাছে পর্যাপ্ত Balance নেই।")
        return

    data = await state.get_data()
    number = data["number"]

    users[user_id]["withdraw_number"] = number

    # Send request to admin
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"w_approve_{user_id}_{amount}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"w_reject_{user_id}_{amount}")
    )
    await bot.send_message(
        ADMIN_ID,
        f"💸 নতুন Withdraw Request:\n\n"
        f"👤 User: {user_id}\n"
        f"📱 Number: {number}\n"
        f"💰 Amount: {amount}৳",
        reply_markup=keyboard
    )

    await message.answer("✅ আপনার Withdraw Request Admin এর কাছে পাঠানো হয়েছে।")
    await state.finish()


# --- Withdraw admin action ---
@dp.callback_query_handler(lambda c: c.data.startswith("w_"))
async def withdraw_admin(callback: types.CallbackQuery):
    parts = callback.data.split("_")
    action, user_id, amount = parts[1], int(parts[2]), int(parts[3])

    if action == "approve":
        users[user_id]["balance"] -= amount
        await bot.send_message(user_id, f"✅ Withdraw Approved!\n💵 {amount}৳ আপনার একাউন্টে পাঠানো হবে।")
    else:
        await bot.send_message(user_id, "❌ Withdraw Rejected.")

    await callback.answer("Done!")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
