from pathlib import Path

from aiogram import Dispatcher, types
from bot.celery_tasks.remove_backgroud import remove_background_from_image


async def remove_bg(message: types.Message):
    text = message.caption
    photo = message.photo[-1]
    filename = f"bot/temp/{message.chat.id}"
    if not Path(filename).exists():
        await photo.download(destination_file=filename)
        if text == "s":
            remove_background_from_image.delay(filename, "webp")
        else:
            remove_background_from_image.delay(filename, "png")
        await message.reply("Запущена обработка изображения...")
    else:
        await message.reply("Уже выполняется, дождитесь окончания")


def register_remove_bg_handlers(dp: Dispatcher):
    dp.register_message_handler(remove_bg, content_types=types.ContentType.PHOTO)
