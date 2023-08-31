from aiogram import Dispatcher

from bot.handlers.admins import register_admin_handlers
from bot.handlers.users import register_chatgpt_handlers
from bot.handlers.users import register_kandinsky_handlers
from bot.handlers.users import register_other_handlers
from bot.handlers.errors import register_error_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_admin_handlers,
        register_error_handlers,
        register_kandinsky_handlers,
        register_other_handlers,
        register_chatgpt_handlers,
    )
    for handler in handlers:
        handler(dp)
