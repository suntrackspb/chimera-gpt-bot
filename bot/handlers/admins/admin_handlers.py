from aiogram import types
from aiogram.dispatcher import Dispatcher

from bot.database.db import MEncode
from bot.utils.constants import db_user, db_day
from bot.utils.msg_templates import ADM_MSG
from bot.main import bot


async def admin_help(message: types.Message):
    db_user.check_user(message)
    await message.answer(ADM_MSG, parse_mode='Markdown')


# @dp.message_handler(commands=['last'])
# async def last_5_messages_handler(message: types.Message):
#     # chat_id = message.chat.id
#     messages = await bot.leave_chat(-1001854884691)
#     print(messages)
#     await message.answer(f"{messages}")


async def user_info(message: types.Message):
    if db_user.check_admin(message.chat.id):
        test = message.text.split(" ", 1)
        chat_id = int(test[1])
        user = await bot.get_chat_member(chat_id=chat_id, user_id=int(chat_id))
        await message.answer(f"{user}")
    else:
        await bot.send_message(message.chat.id, text="Вы не админ!")


async def write_to_user(message: types.Message):
    if db_user.check_admin(message.chat.id):
        test = message.text.split(" ", 2)
        chat_id = int(test[1])
        text = test[2]
        await bot.send_message(chat_id=chat_id, text=text)
    else:
        await bot.send_message(message.chat.id, text="Вы не админ!")


async def users_list(message: types.Message):
    if db_user.check_admin(message.chat.id):
        string = ''
        for user in list(db_user.get_users()):
            string += f"<code>{user['tid']}</code> [@{user['username']}]\n" \
                      f"{user['firstname']} {user['lastname']}\n" \
                      f"token: {user['total_tokens']}, img: {user['imgCount']}, ban: {user['isBlocked']}\n\n"

        await bot.send_message(chat_id=message.chat.id, text=string, parse_mode="HTML")
    else:
        await bot.send_message(message.chat.id, text="Вы не админ!")


async def user_db_info(message: types.Message):
    if db_user.check_admin(message.chat.id):
        test = message.text.split(" ", 1)
        chat_id = int(test[1])
        result = MEncode(db_user.get_user(chat_id)).encode()
        my_string = '\n'.join([f'{key}: <code>{value}</code>' for key, value in result.items()])
        await bot.send_message(chat_id=message.chat.id, text=my_string, parse_mode="HTML")
    else:
        await bot.send_message(message.chat.id, text="Вы не админ!")


async def user_set_limit(message: types.Message):
    if db_user.check_admin(message.chat.id):
        test = message.text.split(" ", 2)
        chat_id = int(test[1])
        limit = int(test[2])
        db_user.set_limit(chat_id, limit)
        await bot.send_message(chat_id=message.chat.id, text="Operation LIMIT complete")
    else:
        await bot.send_message(message.chat.id, text="Вы не админ!")


async def user_drop_limit(message: types.Message):
    if db_user.check_admin(message.chat.id):
        test = message.text.split(" ", 1)
        chat_id = int(test[1])
        db_day.drop_limit(chat_id)
        await bot.send_message(chat_id=message.chat.id, text="Operation DROP complete")
    else:
        await bot.send_message(message.chat.id, text="Вы не админ!")


async def user_set_ban(message: types.Message):
    if db_user.check_admin(message.chat.id):
        test = message.text.split(" ", 1)
        chat_id = int(test[1])
        db_user.set_block(chat_id)
        await bot.send_message(chat_id=message.chat.id, text="Operation BAN complete")
    else:
        await bot.send_message(message.chat.id, text="Вы не админ!")


async def user_set_admin(message: types.Message):
    if db_user.check_admin(message.chat.id):
        test = message.text.split(" ", 1)
        chat_id = int(test[1])
        db_user.set_admin(chat_id)
        await message.answer(text="Operation ADMIN complete")
    else:
        await message.answer(text="Вы не админ!")


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_help, commands="admin")
    dp.register_message_handler(user_info, commands="info")
    dp.register_message_handler(write_to_user, commands="write")
    dp.register_message_handler(users_list, commands="users")
    dp.register_message_handler(user_db_info, commands="user")
    dp.register_message_handler(user_set_limit, commands="limit")
    dp.register_message_handler(user_drop_limit, commands="drop")
    dp.register_message_handler(user_set_ban, commands="ban")
    dp.register_message_handler(user_set_admin, commands="adm")



