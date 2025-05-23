import nest_asyncio
import asyncio
from telegram_handler import start_telegram_bot

nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(start_telegram_bot())
