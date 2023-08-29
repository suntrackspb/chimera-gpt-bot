import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.utils import exceptions as tg_exceptions
from dotenv import load_dotenv, find_dotenv


from keyboards.main_keyboard import get_main_keyboard
from keyboards.style_keyboard import get_style_keyboard
from keyboards.gallery_keyboard import get_gallery_keyboard
from bot.handlers.admins.admin_handlers import register_admins_handlers


load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())


class States(StatesGroup):
    STYLE = State()  # Initial state
    DESC = State()  # State for asking the user's name
    END = State()  # Final state


async def on_startup(dp):
    await bot.send_message(chat_id=os.getenv("ALERTS"), text='Бот запущен')


async def on_shutdown(dp):
    await bot.send_message(chat_id=os.getenv("ALERTS"), text='Бот остановлен')


register_admins_handlers(dp)


if __name__ == '__main__':
    from aiogram import executor

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(on_startup(dp))
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        print(e)
        loop.run_until_complete(on_shutdown(dp))
