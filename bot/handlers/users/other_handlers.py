from aiogram import Dispatcher, types

from bot.loader import bot
from bot.utils.msg_templates import HELP_MSG, BAN_MSG, get_profile_msg, GALLERY_MSG
from bot.utils.constants import bot_messages, db_day, db_user, db_gpt, rm_bg
from bot.keyboards.main_keyboard import get_main_keyboard
from bot.keyboards.gallery_keyboard import get_gallery_keyboard


async def start(message: types.Message):
    db_user.check_user(message)
    await message.answer(HELP_MSG, parse_mode='Markdown', reply_markup=get_main_keyboard())


async def show_gallery(message: types.Message):
    await bot.send_message(message.chat.id, text=GALLERY_MSG, reply_markup=get_gallery_keyboard())


async def new_context(message: types.Message):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        bot_messages[message.chat.id] = []
        await message.answer(text="Контекст предыдущего диалога очищен.", reply_markup=get_main_keyboard())
        db_gpt.add_request(message.chat.id, "CLEAR: =========== ")
    else:
        await bot.send_message(message.chat.id, text=BAN_MSG)


async def profile(message: types.Message):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        user = db_user.get_user(message.chat.id)
        count = db_day.get_count(message.chat.id)
        await bot.send_message(message.chat.id, text=get_profile_msg(user, count), reply_markup=get_main_keyboard())
    else:
        await bot.send_message(message.chat.id, text=BAN_MSG)


async def check_rm_bg(message: types.Message):
    await message.answer(rm_bg)


def register_other_handlers(dp: Dispatcher):
    dp.register_message_handler(profile, commands="profile")
    dp.register_message_handler(profile, lambda message: message.text == "⚙️ Профиль")
    dp.register_message_handler(new_context, commands="new")
    dp.register_message_handler(new_context, lambda message: message.text == "📄 Очистить контекст")
    dp.register_message_handler(show_gallery, commands="gallery")
    dp.register_message_handler(show_gallery, lambda message: message.text == "🖼 Галерея")
    dp.register_message_handler(start, commands=["start", "help"])
    dp.register_message_handler(check_rm_bg, commands="bg")
