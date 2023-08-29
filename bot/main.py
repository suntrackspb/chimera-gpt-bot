import logging
import os

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

from bot.loader import bot, dp
from bot.handlers import register_all_handlers


logging.basicConfig(level=logging.INFO)


class States(StatesGroup):
    STYLE = State()  # Initial state
    DESC = State()  # State for asking the user's name
    END = State()  # Final state


async def on_startup(dp):
    register_all_handlers(dp)
    await bot.send_message(chat_id=os.getenv("ALERTS"), text='Бот запущен')


def start_bot():

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
