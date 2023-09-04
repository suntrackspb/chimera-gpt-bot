import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv

if os.getenv("MODE") == "PROD":
    env = ".env.prod"
else:
    env = ".env.local"

load_dotenv(find_dotenv(env))

bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())
