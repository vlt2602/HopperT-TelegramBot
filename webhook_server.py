from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from config import TELEGRAM_TOKEN
from telegram_handler import status, resume, toggle, setcapital, capital, lastorder, report, addcapital, removecapital, resetcapital, menu, top, resetlog, pause
import asyncio

app = Flask(__name__)

async def process_update(update_json):
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    update = Update.de_json(update_json, application.bot)
    await application.process_update(update)

@app.route(f"/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    asyncio.run(process_update(update))
    return "OK"

if __name__ == "__main__":
    app.run(port=5000)
