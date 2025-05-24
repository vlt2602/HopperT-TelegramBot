import nest_asyncio
import asyncio
from telegram_handler import start_telegram_bot

# Kích hoạt hỗ trợ vòng lặp lồng nhau
nest_asyncio.apply()

if __name__ == "__main__":
    asyncio.run(start_telegram_bot())
