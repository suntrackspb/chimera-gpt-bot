import logging
import os

from aiogram.utils import executor

from bot.loader import bot, dp
from bot.handlers import register_all_handlers


logging.basicConfig(level=logging.INFO)


async def on_startup(dp):
    register_all_handlers(dp)
    await bot.send_message(chat_id=os.getenv("ALERTS"), text='Бот запущен')


def start_bot():
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
