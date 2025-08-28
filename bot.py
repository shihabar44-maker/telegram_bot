# -*- coding: utf-8 -*-
"""
Telegram Bot (Bangla) — Full Run Code (5 Features)
==================================================

Included features:
1) SQLite Database (permanent storage)
2) Referral System (/start <ref>, /refer)
3) Anti-Spam / Security (rate limit)
4) Premium System (VIP users; claim reward multiplier)
5) Multi-Admin Support (roles: owner/admin/helper)

Removed/Not included:
- Daily Bonus ❌
- Auto Payment Gateway ❌

python-telegram-bot >= 20
"""

from __future__ import annotations

import logging
import os
import re
import sqlite3
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ================== CONFIG ==================
TOKEN = os.getenv("BOT_TOKEN", "7890244767:AAE4HRfDjhyLce4feEaK_YCgFaJbVHi_2nA")  # .env/ENV এ রাখুন
OWNER_ID = int(os.getenv("OWNER_ID", "8028396521"))         # আপনার numeric Telegram ID
SUPPORT_GROUP_LINK = os.getenv("SUPPORT_GROUP", "https://t.me/your_group")

# অর্থ সংক্রান্ত সেটিংস
MIN_WITHDRAW = 100                # মিনিমাম উইথড্র
CLAIM_REWARD_BASE = 20            # প্রতি সেল অ্যাপ্রুভে claim base value
REF_REWARD = 10                   # রেফারার বোনাস (একবার, refer set হলে)
PREMIUM_MULTIPLIER = 2            # প্রিমিয়াম ইউজারের ক্লেইমে গুণ (claim-time এ প্রযোজ্য)

DB_PATH = os.getenv("DB_PATH", "bot.db")

# ================== LOGGING ==================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ================== DATABASE ==================
SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    username    TEXT,
    first_name  TEXT,
    balance     INTEGER DEFAULT 0,
    premium     INTEGER DEFAULT 0,
    referred_by INTEGER,
    last_active TEXT
);

CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT PRIMARY KEY,
    user_id  INTEGER NOT NULL,
    base_amt INTEGER NOT NULL,
    created  TEXT
);

CREATE TABLE IF NOT EXISTS withdrawals (
    id        TEXT PRIMARY KEY,
    user_id   INTEGER,
    method    TEXT,
    number    TEXT,
    amount    INTEGER,
    status    TEXT,          -- pending/approved/rejected/paid
    created   TEXT,
    updated   TEXT
);

CREATE TABLE IF NOT EXISTS referrals (
    user_id   INTEGER PRIMARY KEY, -- যার রেফ কোড
    code      TEXT UNIQUE,
    total     INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY,
    role    TEXT CHECK(role IN ('owner','admin','helper'))
);
"""

def db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

# Initialize DB & owner role
with db() as con:
    con.executescript(SCHEMA)
    con.execute(
        "INSERT OR IGNORE INTO admins(user_id, role) VALUES(?, 'owner')",
        (OWNER_ID,),
    )

# ================== UI (Keyboards) ==================
main_menu = ReplyKeyboardMarkup(
    [
        ["🏦 Accounts Sell", "💬 Support Group"],
        ["💰 My Balance", "✅ Withdraw"],
    ],
    resize_keyboard=True
)

sell_menu = ReplyKeyboardMarkup(
    [
        ["📨 Telegram", "📞 WhatsApp"],
        ["⬅️ Back"],
    ],
    resize_keyboard=True
)

back_only = ReplyKeyboardMarkup([["⬅️ Back"]], resize_keyboard=True)

withdraw_menu = ReplyKeyboardMarkup(
    [
        ["📲 Bkash", "💳 Nagad"],
        ["⬅️ Back"],
    ],
    resize_keyboard=True
)

# ===== Conversation States =====
CHOOSE_PLATFORM, ASK_NUMBER, ASK_CODE = range(3)
WD_METHOD, WD_NUMBER = range(3, 5)

# ===== Validators =====
PHONE_RE = re.compile(r'^\+\d{7,15}$')

def is_valid_phone(number: str) -> bool:
    return PHONE_RE.match(number) is not None

# ===== Anti-Spam (simple rate-limit) =====
RATE_WINDOW_SEC = 8
RATE_LIMIT = 5
_last_msgs: Dict[int, list] = {}

async def throttle_and_track(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    now = time.time()
    bucket = _last_msgs.setdefault(user_id, [])
    # keep only recent timestamps
    bucket[:] = [t for t in bucket if now - t <= RATE_WINDOW_SEC]
    bucket.append(now)
    if len(bucket) > RATE_LIMIT:
        # gentle warning once per window
        if int(now) % RATE_WINDOW_SEC == 0:
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="⚠️ অনেক দ্রুত মেসেজ পাঠাচ্ছেন। একটু ধীরে পাঠান।"
                )
            except Exception:
                pass
        # caller should decide to early-return after call
        return True
    return False

# ===== Admin helpers =====
async def get_role(user_id: int) -> Optional[str]:
    with db() as con:
        row = con.execute("SELECT role FROM admins WHERE user_id=?", (user_id,)).fetchone()
        return row["role"] if row else None

async def is_admin(user_id: int) -> Tuple[bool, str]:
    role = await get_role(user_id)
    return (role is not None), (role or "")

def ensure_user_row(u) -> None:
    with db() as con:
        con.execute(
            "INSERT OR IGNORE INTO users(user_id, username, first_name) VALUES(?,?,?)",
            (u.id, u.username, u.first_name),
        )
        con.execute(
            "INSERT OR IGNORE INTO referrals(user_id, code) VALUES(?,?)",
            (u.id, f"ref{u.id}"),
        )

# ===== Global activity tracker =====
async def update_last_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return
    ensure_user_row(user)
    with db() as con:
        con.execute(
            "UPDATE users SET username=?, first_name=?, last_active=? WHERE user_id=?",
            (user.username, user.first_name, datetime.utcnow().isoformat(), user.id),
        )
    # apply throttle (ignore heavy spam)
    too_fast = await throttle_and_track(user.id, context)
    if too_fast:
        return

# ===== /start (with referral capture) =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user_row(user)

    # capture referral code if given: /start <code>
    ref_code = context.args[0] if context.args else None
    if ref_code:
        with db() as con:
            ref = con.execute(
                "SELECT user_id FROM referrals WHERE code=?",
                (ref_code,)
            ).fetchone()

            if ref and ref["user_id"] != user.id:
                # only set once
                cur = con.execute("SELECT referred_by FROM users WHERE user_id=?", (user.id,)).fetchone()
                if cur and cur["referred_by"] is None:
                    con.execute("UPDATE users SET referred_by=? WHERE user_id=?", (ref["user_id"], user.id))
                    # reward referrer once
                    con.execute("UPDATE users SET balance = balance + ? WHERE user_id=?",
                                (REF_REWARD, ref["user_id"]))
                    # increment referral count
                    con.execute(
                        "UPDATE referrals SET total = total + 1 WHERE user_id=?",
                        (ref["user_id"],)
                    )

    await update.message.reply_text(
        "✨ স্বাগতম! নিচের মেনু থেকে অপশন বেছে নিন:",
        reply_markup=main_menu
    )

# ===== /refer — show my referral code & link =====
async def refer_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    ensure_user_row(u)
    with db() as con:
        row = con.execute("SELECT code, total FROM referrals WHERE user_id=?", (u.id,)).fetchone()
        code = row["code"]
        total = row["total"]
    await update.message.reply_text(
        f"🔗 আপনার রেফারেল কোড: `{code}`\n"
        f"▶️ কেউ `/start {code}` দিয়ে বট চালু করলে আপনি {REF_REWARD}৳ পাবেন।\n"
        f"👥 মোট সফল রেফারাল: {total}",
        parse_mode="Markdown"
    )

# ===== /active — last 24h active users =====
async def active_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.utcnow()
    with db() as con:
        rows = con.execute("SELECT first_name, username, last_active FROM users").fetchall()
    active = []
    for r in rows:
        if r["last_active"]:
            ts = datetime.fromisoformat(r["last_active"])
            if now - ts <= timedelta(hours=24):
                name = r["first_name"] or "Unknown"
                uname = f"@{r['username']}" if r["username"] else ""
                active.append(f"{name} {uname}".strip())
    if not active:
        await update.message.reply_text("❌ গত ২৪ ঘন্টায় কোনো Active ইউজার নেই।")
    else:
        await update.message.reply_text(
            "🟢 গত ২৪ ঘন্টায় Active ইউজার:\n\n" + "\n".join(active)
        )

# ===== Static actions =====
async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    ensure_user_row(u)
    with db() as con:
        bal = con.execute("SELECT balance FROM users WHERE user_id=?", (u.id,)).fetchone()["balance"]
        prem = con.execute("SELECT premium FROM users WHERE user_id=?", (u.id,)).fetchone()["premium"]
    tag = " (⭐ Premium)" if prem else ""
    await update.message.reply_text(f"💰 Balance: {bal}৳{tag}")

async def support_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"💬 Support Group: {SUPPORT_GROUP_LINK}")

# ===== Premium controls (admin only) =====
async def premium_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caller = update.effective_user
    ok, role = await is_admin(caller.id)
    if not ok:
        await update.message.reply_text("⛔ এই কমান্ড শুধুমাত্র Admin-দের জন্য।")
        return
    if not context.args:
        await update.message.reply_text("Usage: /premium_on <user_id>")
        return
    tgt = int(context.args[0])
    with db() as con:
        con.execute("UPDATE users SET premium=1 WHERE user_id=?", (tgt,))
    await update.message.reply_text(f"✅ {tgt} এখন Premium।")

async def premium_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caller = update.effective_user
    ok, role = await is_admin(caller.id)
    if not ok:
        await update.message.reply_text("⛔ এই কমান্ড শুধুমাত্র Admin-দের জন্য।")
        return
    if not context.args:
        await update.message.reply_text("Usage: /premium_off <user_id>")
        return
    tgt = int(context.args[0])
    with db() as con:
        con.execute("UPDATE users SET premium=0 WHERE user_id=?", (tgt,))
    await update.message.reply_text(f"✅ {tgt} থেকে Premium সরানো হয়েছে।")

# ===== Admin role mgmt (owner only) =====
async def admin_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caller = update.effective_user
    role = await get_role(caller.id)
    if role != "owner":
        await update.message.reply_text("⛔ এই কমান্ড শুধুমাত্র Owner-এর জন্য।")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /admin_add <user_id> <admin|helper>")
        return
    tgt = int(context.args[0])
    tgt_role = context.args[1].lower()
    if tgt_role not in ("admin", "helper"):
        await update.message.reply_text("⛔ role অবশ্যই admin/helper হতে হবে।")
        return
    with db() as con:
        con.execute("INSERT OR REPLACE INTO admins(user_id, role) VALUES(?,?)", (tgt, tgt_role))
    await update.message.reply_text(f"✅ {tgt} কে {tgt_role} রোলে যুক্ত করা হয়েছে।")

async def admin_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caller = update.effective_user
    role = await get_role(caller.id)
    if role != "owner":
        await update.message.reply_text("⛔ এই কমান্ড শুধুমাত্র Owner-এর জন্য।")
        return
    if not context.args:
        await update.message.reply_text("Usage: /admin_del <user_id>")
        return
    tgt = int(context.args[0])
    with db() as con:
        con.execute("DELETE FROM admins WHERE user_id=? AND role!='owner'", (tgt,))
    await update.message.reply_text(f"✅ {tgt} admin তালিকা থেকে সরানো হয়েছে (owner ছাড়া)।")
  # ===== Sell Flow =====
async def sell_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("একটি প্ল্যাটফর্ম বেছে নিন:", reply_markup=sell_menu)
    return CHOOSE_PLATFORM

async def choose_platform(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📨 Telegram":
        context.user_data["platform"] = "Telegram"
    elif text == "📞 WhatsApp":
        context.user_data["platform"] = "WhatsApp"
    elif text == "⬅️ Back":
        await update.message.reply_text("⬅️ Main Menu", reply_markup=main_menu)
        return ConversationHandler.END
    else:
        await update.message.reply_text("একটি অপশন বেছে নিন:", reply_markup=sell_menu)
        return CHOOSE_PLATFORM

    await update.message.reply_text("📲 আপনার Account Number দিন:", reply_markup=back_only)
    return ASK_NUMBER

async def ask_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Back":
        await update.message.reply_text("একটি প্ল্যাটফর্ম বেছে নিন:", reply_markup=sell_menu)
        return CHOOSE_PLATFORM

    number = update.message.text.strip()
    if len(number) < 5:
        await update.message.reply_text("❌ বৈধ Account Number দিন:", reply_markup=back_only)
        return ASK_NUMBER

    context.user_data["acc_number"] = number
    await update.message.reply_text("Send OTP:", reply_markup=back_only)
    return ASK_CODE

async def complete_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Back":
        return await sell_entry(update, context)

    code = update.message.text.strip()
    if not code.isdigit():
        await update.message.reply_text("❌ Code শুধু সংখ্যা হতে হবে!", reply_markup=back_only)
        return ASK_CODE

    platform = context.user_data.get("platform")
    number = context.user_data.get("acc_number")
    user = update.effective_user

    # Send request to admin/owner
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Approve", callback_data=f"sell_approve_{user.id}")],
            [InlineKeyboardButton("❌ Reject",  callback_data=f"sell_reject_{user.id}")],
        ]
    )
    msg = (
        "🛒 Sell Request\n\n"
        f"👤 User: {user.first_name} ({user.id})\n"
        f"🗂 Platform: {platform}\n"
        f"📲 Account: {number}\n"
        f"🔑 Code: {code}"
    )

    # send to all admins (owner+admins+helpers can see)
    with db() as con:
        admins = con.execute("SELECT user_id FROM admins").fetchall()
    for a in admins:
        try:
            await context.bot.send_message(chat_id=a["user_id"], text=msg, reply_markup=keyboard)
        except Exception:
            pass

    await update.message.reply_text(
        "🔃 Processing your request...\n\n👉 নতুন Account দিতে চাইলে আবার নাম্বার লিখুন অথবা ⬅️ Back চাপুন।",
        reply_markup=back_only
    )
    return ASK_NUMBER

# ===== Withdraw Flow =====
async def withdraw_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ensure_user_row(user)
    with db() as con:
        bal = con.execute("SELECT balance FROM users WHERE user_id=?", (user.id,)).fetchone()["balance"]
    if bal < MIN_WITHDRAW:
        await update.message.reply_text(f"⚠️ মিনিমাম {MIN_WITHDRAW}৳ হলে withdraw করা যাবে।")
        return ConversationHandler.END
    await update.message.reply_text("Withdraw Method নির্বাচন করুন:", reply_markup=withdraw_menu)
    return WD_METHOD

async def choose_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅️ Back":
        await update.message.reply_text("⬅️ Main Menu", reply_markup=main_menu)
        return ConversationHandler.END
    if text not in ("📲 Bkash", "💳 Nagad"):
        await update.message.reply_text("উপরে থেকে একটি মেথড বেছে নিন:", reply_markup=withdraw_menu)
        return WD_METHOD

    context.user_data["wd_method"] = text.replace("📲 ", "").replace("💳 ", "")
    await update.message.reply_text("আপনার নাম্বার দিন (+880... format):", reply_markup=back_only)
    return WD_NUMBER

async def take_withdraw_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip()
    user = update.effective_user

    if number == "⬅️ Back":
        return await withdraw_entry(update, context)
    if not is_valid_phone(number):
        await update.message.reply_text("❌ সঠিক নাম্বার দিন! Format: +CountryCodeXXXXXXXX")
        return WD_NUMBER

    with db() as con:
        bal = con.execute("SELECT balance FROM users WHERE user_id=?", (user.id,)).fetchone()["balance"]

    method = context.user_data.get("wd_method")

    wid = str(uuid.uuid4())
    with db() as con:
        con.execute(
            "INSERT INTO withdrawals(id, user_id, method, number, amount, status, created, updated) VALUES(?,?,?,?,?,?,?,?)",
            (wid, user.id, method, number, bal, "pending", datetime.utcnow().isoformat(), datetime.utcnow().isoformat())
        )

    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅ Approve", callback_data=f"wd_approve_{wid}")],
            [InlineKeyboardButton("❌ Reject",  callback_data=f"wd_reject_{wid}")],
        ]
    )
    msg = (
        "📥 Withdraw Request\n\n"
        f"👤 User: {user.first_name} ({user.id})\n"
        f"💰 Balance: {bal}৳\n"
        f"💳 Method: {method}\n"
        f"📲 Number: {number}\n"
        f"🧾 ID: {wid}"
    )
    with db() as con:
        admins = con.execute("SELECT user_id FROM admins").fetchall()
    for a in admins:
        try:
            await context.bot.send_message(chat_id=a["user_id"], text=msg, reply_markup=keyboard)
        except Exception:
            pass

    await update.message.reply_text("🔃 Withdraw Request Pending...", reply_markup=main_menu)
    return ConversationHandler.END

# ===== Admin Callback Handlers =====
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_", 2)
    category = data[0]  # 'sell' or 'wd'
    action   = data[1]  # 'approve' | 'reject'
    slug     = data[2]

    caller = query.from_user
    ok, role = await is_admin(caller.id)
    if not ok:
        await query.edit_message_text("⛔ কেবল Admin-রা এটি করতে পারবেন।")
        return

    if category == "sell":
        user_id = int(slug)
        if action == "approve":
            # create a claim with BASE amount (premium multiplier at claim-time)
            claim_id = str(uuid.uuid4())
            with db() as con:
                con.execute(
                    "INSERT INTO claims(claim_id, user_id, base_amt, created) VALUES(?,?,?,?)",
                    (claim_id, user_id, CLAIM_REWARD_BASE, datetime.utcnow().isoformat())
                )
            await context.bot.send_message(
                chat_id=user_id,
                text="✅ Account Sell Successful!\n\n💰 Claim করতে নিচের বাটন চাপুন:",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🎁 Claim", callback_data=f"claim_{user_id}_{claim_id}")]]
                )
            )
            await query.edit_message_text("✅ Approved & User Notified.")
        else:
            await context.bot.send_message(chat_id=user_id, text="❌ Account Sell Rejected!")
            await query.edit_message_text("❌ Rejected & User Notified.")

    elif category == "wd":
        wid = slug  # withdrawal id
        with db() as con:
            rec = con.execute("SELECT user_id, amount, status FROM withdrawals WHERE id=?", (wid,)).fetchone()
        if not rec:
            await query.edit_message_text("⚠️ Invalid withdrawal ID.")
            return
        user_id = rec["user_id"]

        if action == "approve":
            with db() as con:
                # zero out user balance, mark withdrawal approved (simulate paid)
                con.execute("UPDATE users SET balance=0 WHERE user_id=?", (user_id,))
                con.execute(
                    "UPDATE withdrawals SET status='approved', updated=? WHERE id=?",
                    (datetime.utcnow().isoformat(), wid)
                )
            await context.bot.send_message(chat_id=user_id, text="✅ Withdraw Approved!\n💰 Balance: 0৳")
            await query.edit_message_text("✅ Withdraw Approved & User Notified.")
        else:
            with db() as con:
                con.execute(
                    "UPDATE withdrawals SET status='rejected', updated=? WHERE id=?",
                    (datetime.utcnow().isoformat(), wid)
                )
            await context.bot.send_message(chat_id=user_id, text="❌ Withdraw Rejected.")
            await query.edit_message_text("❌ Withdraw Rejected & User Notified.")

# ===== Claim Button Callback =====
async def claim_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        _, user_id_str, claim_id = query.data.split("_", 2)
        user_id = int(user_id_str)
    except Exception:
        await query.edit_message_text("⚠️ Invalid claim.")
        return

    # fetch claim; if exists, pay with premium multiplier; then delete claim
    with db() as con:
        row = con.execute("SELECT user_id, base_amt FROM claims WHERE claim_id=?", (claim_id,)).fetchone()
        if not row or row["user_id"] != user_id:
            await query.edit_message_text("⚠️ Already Claimed or Invalid.")
            return

        prem = con.execute("SELECT premium FROM users WHERE user_id=?", (user_id,)).fetchone()["premium"]
        final_amt = row["base_amt"] * (PREMIUM_MULTIPLIER if prem else 1)

        con.execute("DELETE FROM claims WHERE claim_id=?", (claim_id,))
        con.execute("UPDATE users SET balance = balance + ? WHERE user_id=?", (final_amt, user_id))
        bal = con.execute("SELECT balance FROM users WHERE user_id=?", (user_id,)).fetchone()["balance"]

    # remove the specific button from message UI
    old_keyboard = query.message.reply_markup.inline_keyboard if query.message.reply_markup else []
    new_keyboard = []
    for row in old_keyboard:
        new_row = [btn for btn in row if btn.callback_data != query.data]
        if new_row:
            new_keyboard.append(new_row)

    await query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(new_keyboard) if new_keyboard else None
    )
    await context.bot.send_message(
        chat_id=user_id,
        text=f"🎁 Claim সফল! প্রাপ্তি: {final_amt}৳\n💰 নতুন Balance: {bal}৳"
    )

# ===== Menu Message Handlers =====
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🏦 Accounts Sell":
        return await sell_entry(update, context)
    elif text == "💬 Support Group":
        return await support_group(update, context)
    elif text == "💰 My Balance":
        return await show_balance(update, context)
    elif text == "✅ Withdraw":
        return await withdraw_entry(update, context)
    else:
        await update.message.reply_text("❓ বোঝা গেল না। নিচের মেনু থেকে বেছে নিন।", reply_markup=main_menu)

# ===== Build & Run App =====
def main():
    if not TOKEN or TOKEN == "CHANGE_ME_ENV_BOT_TOKEN":
        raise RuntimeError("Please set BOT_TOKEN in environment.")

    app = Application.builder().token(TOKEN).build()

    # Track activity & throttle
    app.add_handler(MessageHandler(filters.ALL, update_last_active), group=0)
    app.add_handler(CallbackQueryHandler(update_last_active), group=0)

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("refer", refer_cmd))
    app.add_handler(CommandHandler("active", active_users_cmd))

    app.add_handler(CommandHandler("premium_on", premium_on))
    app.add_handler(CommandHandler("premium_off", premium_off))
    app.add_handler(CommandHandler("admin_add", admin_add))
    app.add_handler(CommandHandler("admin_del", admin_del))

    # Sell Conversation
    sell_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🏦 Accounts Sell$"), sell_entry)],
        states={
            CHOOSE_PLATFORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_platform)],
            ASK_NUMBER:      [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_code)],
            ASK_CODE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_sell)],
        },
        fallbacks=[MessageHandler(filters.Regex("^⬅️ Back$"), sell_entry)],
    )
    app.add_handler(sell_conv)

    # Withdraw Conversation
    wd_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^✅ Withdraw$"), withdraw_entry)],
        states={
            WD_METHOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_method)],
            WD_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, take_withdraw_number)],
        },
        fallbacks=[MessageHandler(filters.Regex("^⬅️ Back$"), withdraw_entry)],
    )
    app.add_handler(wd_conv)

    # Inline callbacks
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(sell|wd)_"))
    app.add_handler(CallbackQueryHandler(claim_callback, pattern="^claim_"))

    # Generic menu (for any stray text that matches menu labels)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))

    logger.info("Bot started polling...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
