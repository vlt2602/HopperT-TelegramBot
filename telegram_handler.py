from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from config import TELEGRAM_TOKEN, ALLOWED_CHAT_ID
import builtins
import pandas as pd

builtins.bot_active = True
builtins.capital_limit = 500
builtins.last_order = None

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    state = "🟢 ĐANG CHẠY" if builtins.bot_active else "🔴 ĐANG DỪNG"
    await update.message.reply_text(f"✅ HopperT đang hoạt động!\nTrạng thái bot: {state}")

async def capital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    allowed_cap = builtins.capital_limit
    await update.message.reply_text(f"💰 Vốn giới hạn: {allowed_cap} USDT")

async def lastorder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    msg = builtins.last_order or "⚠️ Chưa có lệnh nào gần đây."
    await update.message.reply_text(f"📦 Lệnh gần nhất:\n{msg}")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != ALLOWED_CHAT_ID: return
    buttons = [["/status", "/capital", "/lastorder", "/menu"]]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("📋 Menu điều khiển HopperT:", reply_markup=markup)

async def start_telegram_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("capital", capital))
    app.add_handler(CommandHandler("lastorder", lastorder))
    app.add_handler(CommandHandler("menu", menu))
    print("✅ Telegram bot đã sẵn sàng...")
    await app.run_polling()
