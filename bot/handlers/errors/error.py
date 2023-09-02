import logging
import os

from aiogram import Dispatcher
from aiogram.utils import exceptions as tg_exceptions
from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError,
                                      CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound,
                                      MessageTextIsEmpty, RetryAfter,
                                      CantParseEntities, MessageCantBeDeleted)

from bot.loader import bot
from bot.utils.msg_templates import GPT_ERROR


async def error_handler(update, exception):
    """
        Exceptions handler. Catches all exceptions within task factory tasks.
        :param update:
        :param exception:
        :return: stdout logging
        """
    if isinstance(exception, CantDemoteChatCreator):
        logging.exception("Can't demote chat creator")
        return True

    if isinstance(exception, MessageNotModified):
        logging.exception('Message is not modified')
        return True
    if isinstance(exception, MessageCantBeDeleted):
        logging.exception('Message cant be deleted')
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        logging.exception('Message to delete not found')
        return True

    if isinstance(exception, MessageTextIsEmpty):
        logging.exception('MessageTextIsEmpty')
        return True

    if isinstance(exception, Unauthorized):
        logging.exception(f'Unauthorized: {exception}')
        return True

    if isinstance(exception, InvalidQueryID):
        logging.exception(f'InvalidQueryID: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, RetryAfter):
        logging.exception(f'RetryAfter: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, CantParseEntities):
        logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True

    logging.exception(f'Update: {update} \n{exception}')

    # if isinstance(exception, tg_exceptions.TelegramAPIError):
    #     print(f'Ошибка у пользователя: {update.message.chat.id}')
    #     await bot.send_message(chat_id=os.getenv("ALERTS"), text=f'Ошибка у пользователя: {update.message.chat.id}')
    #     await bot.send_message(chat_id=update.message.chat.id, text=GPT_ERROR)
    # else:
    #     raise exception


def register_error_handlers(dp: Dispatcher):
    dp.register_errors_handler(error_handler)
