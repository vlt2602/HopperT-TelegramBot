from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from config import TELEGRAM_TOKEN
from telegram_handler import status, resume, toggle, setcapital, capital, lastorder, report, addcapital, removecapital, resetcapital, menu, top, resetlog, pause
import asyncio

app = Flask(__name__)

# Khởi tạo application 1 lần duy nhất
application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
application.add_handler(CommandHandler("status", status))
application.add_handler(CommandHandler("resume", resume))
application.add_handler(CommandHandler("toggle", toggle))
application.add_handler(CommandHandler("setcapital", setcapital))
application.add_handler(CommandHandler("capital", capital))
application.add_handler(CommandHandler("lastorder", lastorder))
application.add_handler(CommandHandler("report", report))
application.add_handler(CommandHandler("addcapital", addcapital))
application.add_handler(CommandHandler("removecapital", removecapital))
application.add_handler(CommandHandler("resetcapital", resetcapital))
application.add_handler(CommandHandler("menu", menu))
application.add_handler(CommandHandler("top", top))
application.add_handler(CommandHandler("resetlog", resetlog))
application.add_handler(CommandHandler("pause", pause))

# Khởi tạo Application trước khi xử lý update
asyncio.run(application.initialize())

async def process_update(update_json):
    update = Update.de_json(update_json, application.bot)
    await application.process_update(update)

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    asyncio.run(process_update(update))
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
