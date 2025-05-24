import nest_asyncio
import asyncio
from telegram_handler import start_telegram_bot

# Kích hoạt hỗ trợ vòng lặp lồng nhau
nest_asyncio.apply()

# Khởi chạy bot Telegram
asyncio.get_event_loop().run_until_complete(start_telegram_bot())
