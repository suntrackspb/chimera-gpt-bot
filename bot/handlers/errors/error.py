import os

from aiogram import Dispatcher
from aiogram.utils import exceptions as tg_exceptions

from bot.loader import bot
from bot.utils.msg_templates import GPT_ERROR


async def error_handler(update, exception):
    if isinstance(exception, tg_exceptions.TelegramAPIError):
        print(f'Ошибка у пользователя: {update.message.chat.id}')
        await bot.send_message(chat_id=os.getenv("ALERTS"), text=f'Ошибка у пользователя: {update.message.chat.id}')
        await bot.send_message(chat_id=update.message.chat.id, text=GPT_ERROR)
    else:
        raise exception


def register_error_handlers(dp: Dispatcher):
    dp.register_errors_handler(error_handler)
