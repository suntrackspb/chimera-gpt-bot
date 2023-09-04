from aiogram import Dispatcher, types


async def remove_bg(message: types.Message):
    pass


def register_remove_bg_handlers(dp: Dispatcher):
    dp.register_message_handler(remove_bg, content_types=types.ContentType.PHOTO)
