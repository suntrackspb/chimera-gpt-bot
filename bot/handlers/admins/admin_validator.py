from aiogram import types
from bot.utils.constants import db_user


def validate_user_is_admin(message: types.Message):
    if db_user.check_admin(message.chat.id):
        return True
    else:
        message.answer(text="Вы не администратор")

