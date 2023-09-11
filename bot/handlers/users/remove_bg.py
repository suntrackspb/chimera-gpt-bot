import os
from pathlib import Path

from aiogram import Dispatcher, types
from bot.celery_tasks.rembg_local import local_remove_background
from bot.celery_tasks.rembg_api import api_remove_background


async def remove_bg(message: types.Message):
    photo = message.photo[-1]
    filename = f"bot/temp/{message.chat.id}"
    if not Path(filename).exists():
        await photo.download(destination_file=filename)
        if os.getenv("REMBG_API"):
            api_remove_background.delay(message.chat.id, message.caption, filename)
        else:
            local_remove_background.delay(message.chat.id, message.caption, filename)
        await message.reply("Запущена обработка изображения...")
    else:
        await message.reply("Уже выполняется, дождитесь окончания")


def register_remove_bg_handlers(dp: Dispatcher):
    dp.register_message_handler(remove_bg, content_types=types.ContentType.PHOTO)
