import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv

MODE = os.getenv("MODE")

if MODE == "PROD":
    env = ".env.prod"
elif MODE == "DOCKER":
    env = ".env.docker"
elif MODE == "LOCAL":
    env = ".env.local"
else:
    env = ".env.local"

load_dotenv(find_dotenv(env))

bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())
