from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN, ALLOWED_CHAT_ID
import builtins
import csv
import os
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Biến trạng thái toàn cục
builtins.panic_mode = False
builtins.loss_streak = 0
builtins.capital_limit = 500
builtins.capital_limit_init = 500
builtins.bot_active = True
builtins.last_order = None

def check_auth(update: Update):
    return update.effective_chat.id == ALLOWED_CHAT_ID

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    state = "🟢 ĐANG CHẠY" if builtins.bot_active else "🔴 ĐANG DỪNG"
    await update.message.reply_text(f"✅ HopperT đang hoạt động!\nTrạng thái bot: {state}")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    builtins.panic_mode = False
    builtins.loss_streak = 0
    await update.message.reply_text("✅ Đã gỡ Panic Stop. Tiếp tục giao dịch.")

async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    builtins.bot_active = not builtins.bot_active
    state = "🟢 Bot ĐANG CHẠY" if builtins.bot_active else "🔴 Bot ĐÃ DỪNG"
    await update.message.reply_text(f"⚙️ Trạng thái bot: {state}")

async def setcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    try:
        amount = float(context.args[0])
        if amount < 0:
            await update.message.reply_text("❌ Vui lòng nhập số dương.")
            return
        builtins.capital_limit = amount
        builtins.capital_limit_init = amount
        await update.message.reply_text(f"✅ Cập nhật vốn tối đa: {amount} USDT")
    except:
        await update.message.reply_text("❌ Sai cú pháp. Dùng: /setcapital [số_usdt]")

async def capital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    await update.message.reply_text(f"💰 Vốn giới hạn: {builtins.capital_limit} USDT")

async def addcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    builtins.capital_limit += 100
    builtins.capital_limit_init += 100
    await update.message.reply_text(f"➕ Tăng vốn +100\n👉 Vốn hiện tại: {builtins.capital_limit} USDT")

async def removecapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    builtins.capital_limit = max(0, builtins.capital_limit - 100)
    builtins.capital_limit_init = max(0, builtins.capital_limit_init - 100)
    await update.message.reply_text(f"➖ Giảm vốn -100\n👉 Vốn hiện tại: {builtins.capital_limit} USDT")

async def resetcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    builtins.capital_limit = 500
    builtins.capital_limit_init = 500
    await update.message.reply_text("🔁 Reset vốn về mặc định: 500 USDT")

async def lastorder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    msg = builtins.last_order or "⚠️ Chưa có lệnh nào gần đây."
    await update.message.reply_text(f"📦 Lệnh gần nhất:\n{msg}")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    await update.message.reply_text("📅 Báo cáo tự động lúc 05:00 hàng ngày & 05:01 Chủ nhật.")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    try:
        if not os.path.exists("strategy_log.csv"):
            await update.message.reply_text("⚠️ Chưa có dữ liệu chiến lược.")
            return
        summary = {}
        with open("strategy_log.csv", newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) < 5:
                    continue
                strategy, pnl = row[2], row[4]
                try:
                    pnl = float(pnl)
                except ValueError:
                    continue
                summary[strategy] = summary.get(strategy, 0) + pnl
        if not summary:
            await update.message.reply_text("⚠️ Chưa có dữ liệu chiến lược.")
            return
        best = max(summary, key=summary.get)
        await update.message.reply_text(f"🏆 Chiến lược tốt nhất: {best} ({summary[best]:.2f} USDT)")
    except Exception as e:
        logger.error(f"Lỗi /top: {e}")
        await update.message.reply_text(f"❌ Lỗi /top: {e}")

async def resetlog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    try:
        open("strategy_log.csv", "w").close()
        await update.message.reply_text("🗑 Đã xoá toàn bộ log chiến lược.")
    except:
        await update.message.reply_text("❌ Không thể xoá file log.")

async def pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    builtins.bot_active = False
    await update.message.reply_text("⏸ Bot đã tạm dừng. Gõ /resume để chạy lại.")

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    buttons = [["/status", "/toggle", "/resume", "/pause"],
               ["/capital", "/setcapital 500", "/lastorder"],
               ["/addcapital", "/removecapital", "/report"],
               ["/top", "/resetlog", "/menu"]]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text("📋 Menu điều khiển HopperT:", reply_markup=markup)

async def start_telegram_bot():
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("status", status))
        app.add_handler(CommandHandler("resume", resume))
        app.add_handler(CommandHandler("toggle", toggle))
        app.add_handler(CommandHandler("setcapital", setcapital))
        app.add_handler(CommandHandler("capital", capital))
        app.add_handler(CommandHandler("lastorder", lastorder))
        app.add_handler(CommandHandler("report", report))
        app.add_handler(CommandHandler("addcapital", addcapital))
        app.add_handler(CommandHandler("removecapital", removecapital))
        app.add_handler(CommandHandler("resetcapital", resetcapital))
        app.add_handler(CommandHandler("menu", menu))
        app.add_handler(CommandHandler("top", top))
        app.add_handler(CommandHandler("resetlog", resetlog))
        app.add_handler(CommandHandler("pause", pause))
        logger.info("✅ Telegram bot đã sẵn sàng...")
        await app.run_polling()
    except Exception as e:
        logger.error(f"❌ Lỗi khởi động bot: {e}")
