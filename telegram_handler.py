from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN, ALLOWED_CHAT_ID
import csv
import os
import json
import logging

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATUS_FILE = "status.json"

def read_status():
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "w") as f:
            json.dump({
                "panic_mode": False,
                "loss_streak": 0,
                "capital_limit": 500,
                "capital_limit_init": 500,
                "bot_active": True,
                "last_order": None
            }, f)
    with open(STATUS_FILE, "r") as f:
        return json.load(f)

def write_status(status):
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f)

def check_auth(update: Update):
    return update.effective_chat.id == ALLOWED_CHAT_ID

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    status_data = read_status()
    state = "🟢 ĐANG CHẠY" if status_data["bot_active"] else "🔴 ĐANG DỪNG"
    await update.message.reply_text(f"✅ HopperT đang hoạt động!\nTrạng thái bot: {state}")

async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    status_data = read_status()
    status_data["panic_mode"] = False
    status_data["loss_streak"] = 0
    write_status(status_data)
    await update.message.reply_text("✅ Đã gỡ Panic Stop. Tiếp tục giao dịch.")

async def toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    status_data = read_status()
    status_data["bot_active"] = not status_data["bot_active"]
    write_status(status_data)
    state = "🟢 Bot ĐANG CHẠY" if status_data["bot_active"] else "🔴 Bot ĐÃ DỪNG"
    await update.message.reply_text(f"⚙️ Trạng thái bot: {state}")

async def setcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    status_data = read_status()
    try:
        amount = float(context.args[0])
        if amount < 0:
            await update.message.reply_text("❌ Vui lòng nhập số dương.")
            return
        status_data["capital_limit"] = amount
        status_data["capital_limit_init"] = amount
        write_status(status_data)
        await update.message.reply_text(f"✅ Cập nhật vốn tối đa: {amount} USDT")
    except:
        await update.message.reply_text("❌ Sai cú pháp. Dùng: /setcapital [số_usdt]")

async def capital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    status_data = read_status()
    await update.message.reply_text(f"💰 Vốn giới hạn: {status_data['capital_limit']} USDT")

async def addcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    status_data = read_status()
    status_data["capital_limit"] += 100
    status_data["capital_limit_init"] += 100
    write_status(status_data)
    await update.message.reply_text(f"➕ Tăng vốn +100\n👉 Vốn hiện tại: {status_data['capital_limit']} USDT")

async def removecapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    status_data = read_status()
    status_data["capital_limit"] = max(0, status_data["capital_limit"] - 100)
    status_data["capital_limit_init"] = max(0, status_data["capital_limit_init"] - 100)
    write_status(status_data)
    await update.message.reply_text(f"➖ Giảm vốn -100\n👉 Vốn hiện tại: {status_data['capital_limit']} USDT")

async def resetcapital(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    status_data = read_status()
    status_data["capital_limit"] = 500
    status_data["capital_limit_init"] = 500
    write_status(status_data)
    await update.message.reply_text("🔁 Reset vốn về mặc định: 500 USDT")

async def lastorder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_auth(update): return
    status_data = read_status()
    msg = status_data["last_order"] or "⚠️ Chưa có lệnh nào gần đây."
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
    status_data = read_status()
    status_data["bot_active"] = False
    write_status(status_data)
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
