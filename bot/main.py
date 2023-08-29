import asyncio
import base64
import io
import logging
import os
import re
import textwrap
from io import BytesIO

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.utils import exceptions as tg_exceptions
from dotenv import load_dotenv, find_dotenv

from database.db import MEncode

from utils.converters import convert_voice_to_text, convert_text_to_voice
from utils.chimera_api import make_request
from utils.kandinsky_api import run_generate, get_image, save_image
from utils.msg_templates import HELP_MSG, ADM_MSG, BAN_MSG, get_profile_msg, styles, GPT_ERROR, GALLERY_MSG
from utils.constants import bot_messages, block, db_day, db_user, db_gpt, db_img

from keyboards.main_keyboard import get_main_keyboard
from keyboards.style_keyboard import get_style_keyboard
from keyboards.gallery_keyboard import get_gallery_keyboard
from bot.handlers.admins.admin_handlers import register_admins_handlers


load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)


# async def update_messages(msg, uid, role, content):
#     if msg.get(uid) is None:
#         msg[uid] = [{'role': role, 'content': content}]
#     else:
#         if len(msg.get(uid)) >= 10:
#             if msg[uid][0]['role'] == 'system':
#                 msg[uid].pop(1)
#             else:
#                 msg[uid].pop(0)
#         msg[uid].append({'role': role, 'content': content})


bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())


class States(StatesGroup):
    STYLE = State()  # Initial state
    DESC = State()  # State for asking the user's name
    END = State()  # Final state


async def on_startup(dp):
    await bot.send_message(chat_id=os.getenv("ALERTS"), text='Бот запущен')


async def on_shutdown(dp):
    await bot.send_message(chat_id=os.getenv("ALERTS"), text='Бот остановлен')


async def error_handler(update, exception):
    if isinstance(exception, tg_exceptions.TelegramAPIError):
        print(f'Ошибка у пользователя: {update.message.chat.id}')
        await bot.send_message(chat_id=os.getenv("ALERTS"), text=f'Ошибка у пользователя: {update.message.chat.id}')
        await bot.send_message(chat_id=update.message.chat.id, text=GPT_ERROR)
    else:
        raise exception


dp.register_errors_handler(error_handler)

register_admins_handlers(dp)


async def generate_image(style, desc, tlg):
    img_id = await run_generate(style, desc)
    if img_id is not False:
        data = await get_image(img_id)
        file = await save_image(data, tlg)
        return {"filename": file, "image": io.BytesIO(base64.b64decode(data))}


@dp.message_handler(lambda message: message.text == "🖼 Галерея")
async def create_image(message: types.Message):
    await bot.send_message(message.chat.id, text=GALLERY_MSG, reply_markup=get_main_keyboard())


@dp.message_handler(commands=["start", "help"])
async def start(message: types.Message):
    db_user.check_user(message)
    await message.answer(HELP_MSG, parse_mode='Markdown', reply_markup=get_main_keyboard())


@dp.message_handler(lambda message: message.text == "🎨 Генерация изображения")
@dp.message_handler(commands="img")
async def create_image(message: types.Message):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        if block.get(message.chat.id) is None:
            block[message.chat.id] = True
            text = 'Выберите стиль:'
            await bot.delete_message(message.chat.id, message.message_id)
            await bot.send_message(message.chat.id, text=text, reply_markup=get_style_keyboard())
        else:
            await bot.send_message(message.chat.id, text="Вы уже генерируете изображение...")
    else:
        await bot.send_message(message.chat.id, text=BAN_MSG)


@dp.callback_query_handler(lambda query: re.match('[0-9_]+', query.data))
async def public_to_gallery(query: types.CallbackQuery):
    filename = query.data
    db_img.update_public(filename)
    await bot.edit_message_text(text='Посмотреть можно тут:',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id, reply_markup=get_gallery_keyboard())


@dp.callback_query_handler(lambda query: query.data)
async def allow_profile(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == 'cancel':
        block[callback_query.message.chat.id] = None
        await States.DESC.set()
        await state.finish()
        await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
        msg = await bot.send_message(callback_query.message.chat.id, "Генерация изображения отменена",
                                     reply_markup=get_main_keyboard())
        return
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.message.chat.id, "Введите запрос", reply_markup=types.ReplyKeyboardRemove())
    style = callback_query.data
    await state.update_data(style=style)
    await States.STYLE.set()
    await state.update_data(state="desc")


@dp.message_handler(state=States.STYLE)
async def enter_prompt(message: types.Message, state: FSMContext):
    try:
        description = message.text.replace("\n", "").strip()
        data = await state.get_data()
        style_name = data.get('style')
        # style_code = styles.get(style_name)
        await States.DESC.set()
        await state.finish()
        # await write_log(message.chat.id, f"PICTURE: {description}")
        answer = "✅ Запрос принят, генерируем изображение... 💤 "
        last_message = await bot.send_message(message.chat.id, text=answer)
        bin_photo = await generate_image(style_name, description, message.chat.id)
        db_img.add_row(message.chat.id, bin_photo['filename'], description, styles[style_name])
        await last_message.delete()
        public_markup = types.InlineKeyboardMarkup()
        public_markup.add(types.InlineKeyboardButton(text='Опубликовать', callback_data=bin_photo['filename']))
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.delete_message(message.chat.id, message.message_id - 1)

        await bot.send_photo(chat_id=message.chat.id,
                             photo=types.InputFile(bin_photo['image'], filename='image.jpg'),
                             caption=f'Style: {styles[style_name]}\nPrompt: ```python {description}```',
                             reply_markup=get_main_keyboard(),
                             parse_mode='MarkdownV2')
        await bot.send_message(chat_id=message.chat.id,
                               text="Вы можете поделиться этим изображением, опубликовав его в нашей галереи:",
                               reply_markup=public_markup)

    except Exception as ex:
        print(ex)
    finally:
        block[message.chat.id] = None


@dp.message_handler(commands="voice")
async def voice(message: types.Message):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        text = message.text.removeprefix('/voice ')
        audio = convert_text_to_voice(text)
        # await write_log(message.chat.id, f"GENERATE: {text}")
        db_gpt.add_request(message.chat.id, f"GENERATE: {text}")
        await bot.send_voice(chat_id=message.chat.id, voice=audio, reply_markup=get_main_keyboard())
    else:
        await bot.send_message(message.chat.id, text=BAN_MSG)


@dp.message_handler(lambda message: message.text == "⚙️ Профиль")
@dp.message_handler(commands="profile")
async def profile(message: types.Message):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        user = db_user.get_user(message.chat.id)
        count = db_day.get_count(message.chat.id)
        await bot.send_message(message.chat.id, text=get_profile_msg(user, count), reply_markup=get_main_keyboard())
    else:
        await bot.send_message(message.chat.id, text=BAN_MSG)


@dp.message_handler(lambda message: message.text == "📄 Очистить контекст")
@dp.message_handler(commands="new")
async def new_context(message: types.Message):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        bot_messages[message.chat.id] = []
        await message.answer(text="Контекст предыдущего диалога очищен.", reply_markup=get_main_keyboard())
        db_gpt.add_request(message.chat.id, "CLEAR: =========== ")
    else:
        await bot.send_message(message.chat.id, text=BAN_MSG)


# @dp.message_handler(commands="add")
# async def add_context(message: types.Message):
#     db_user.check_user(message)
#     if not db_user.check_block(message.chat.id):
#         text = message.text.removeprefix('/add ')
#         if text != '/add':
#             bot_messages[message.chat.id] = []
#             await update_messages(bot_messages, message.chat.id, "system", text)
#             await message.answer(f"Установлен system context {text}", reply_markup=get_main_keyboard())
#             db_gpt.add_request(message.chat.id, f"SYSTEM: {text}")
#             db_gpt.add_request(message.chat.id, text)
#         else:
#             await message.answer(text=f"Необходимо указать как бот должен себя вести \n"
#                                       f"Например: _/add Действуй как юрист._")
#     else:
#         await bot.send_message(message.chat.id, text=BAN_MSG)


@dp.message_handler(commands="role")
async def new_context(message: types.Message):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        if bot_messages.get(message.chat.id) is not None:
            if len(bot_messages.get(message.chat.id)) > 0 and bot_messages[message.chat.id][0]['role'] == 'system':
                await message.answer(bot_messages[message.chat.id][0], reply_markup=get_main_keyboard())
            else:
                await message.answer("Конкретная роль ещё не была установлена.\nСмотри /help")
        else:
            await message.answer("Конкретная роль ещё не была установлена.\nСмотри /help")
    else:
        await message.answer(text=BAN_MSG)





#############################
# ADMIN COMMANDS
#############################


# @dp.message_handler(commands="admin")
# async def admin_help(message: types.Message):
#     db_user.check_user(message)
#     await message.answer(ADM_MSG, parse_mode='Markdown')


# @dp.message_handler(commands=['last'])
# async def last_5_messages_handler(message: types.Message):
#     # chat_id = message.chat.id
#     messages = await bot.leave_chat(-1001854884691)
#     print(messages)
#     await message.answer(f"{messages}")


# @dp.message_handler(commands="info")
# async def user_info(message: types.Message):
#     if db_user.check_admin(message.chat.id):
#         test = message.text.split(" ", 1)
#         chat_id = int(test[1])
#         user = await bot.get_chat_member(chat_id=chat_id, user_id=int(chat_id))
#         await message.answer(f"{user}")
#     else:
#         await bot.send_message(message.chat.id, text="Вы не админ!")
#
#
# @dp.message_handler(commands="write")
# async def write_to_user(message: types.Message):
#     if db_user.check_admin(message.chat.id):
#         test = message.text.split(" ", 2)
#         chat_id = int(test[1])
#         text = test[2]
#         await bot.send_message(chat_id=chat_id, text=text)
#     else:
#         await bot.send_message(message.chat.id, text="Вы не админ!")
#
#
# @dp.message_handler(commands="users")
# async def users_list(message: types.Message):
#     if db_user.check_admin(message.chat.id):
#         string = ''
#         for user in list(db_user.get_users()):
#             string += f"<code>{user['tid']}</code> [@{user['username']}]\n" \
#                       f"{user['firstname']} {user['lastname']}\n" \
#                       f"token: {user['total_tokens']}, img: {user['imgCount']}, ban: {user['isBlocked']}\n\n"
#
#         await bot.send_message(chat_id=message.chat.id, text=string, parse_mode="HTML")
#     else:
#         await bot.send_message(message.chat.id, text="Вы не админ!")
#
#
# @dp.message_handler(commands="user")
# async def user_db_info(message: types.Message):
#     if db_user.check_admin(message.chat.id):
#         test = message.text.split(" ", 1)
#         chat_id = int(test[1])
#         result = MEncode(db_user.get_user(chat_id)).encode()
#         my_string = '\n'.join([f'{key}: <code>{value}</code>' for key, value in result.items()])
#         await bot.send_message(chat_id=message.chat.id, text=my_string, parse_mode="HTML")
#     else:
#         await bot.send_message(message.chat.id, text="Вы не админ!")
#
#
# @dp.message_handler(commands="limit")
# async def user_db_info(message: types.Message):
#     if db_user.check_admin(message.chat.id):
#         test = message.text.split(" ", 2)
#         chat_id = int(test[1])
#         limit = int(test[2])
#         db_user.set_limit(chat_id, limit)
#         await bot.send_message(chat_id=message.chat.id, text="Operation LIMIT complete")
#     else:
#         await bot.send_message(message.chat.id, text="Вы не админ!")
#
#
# @dp.message_handler(commands="drop")
# async def user_db_info(message: types.Message):
#     if db_user.check_admin(message.chat.id):
#         test = message.text.split(" ", 1)
#         chat_id = int(test[1])
#         db_day.drop_limit(chat_id)
#         await bot.send_message(chat_id=message.chat.id, text="Operation DROP complete")
#     else:
#         await bot.send_message(message.chat.id, text="Вы не админ!")
#
#
# @dp.message_handler(commands="ban")
# async def user_db_info(message: types.Message):
#     if db_user.check_admin(message.chat.id):
#         test = message.text.split(" ", 1)
#         chat_id = int(test[1])
#         db_user.set_block(chat_id)
#         await bot.send_message(chat_id=message.chat.id, text="Operation BAN complete")
#     else:
#         await bot.send_message(message.chat.id, text="Вы не админ!")
#
#
# @dp.message_handler(commands="adm")
# async def user_db_info(message: types.Message):
#     if db_user.check_admin(message.chat.id):
#         test = message.text.split(" ", 1)
#         chat_id = int(test[1])
#         db_user.set_admin(chat_id)
#         await bot.send_message(chat_id=message.chat.id, text="Operation ADMIN complete")
#     else:
#         await bot.send_message(message.chat.id, text="Вы не админ!")


#############################
# GPT HANDLERS
#############################


# @dp.message_handler(content_types=types.ContentType.VOICE)
# async def handle_voice_message(message: types.Message):
#     db_user.check_user(message)
#     if not db_user.check_block(message.chat.id):
#         if db_user.check_limit(message.chat.id):
#             file = await bot.get_file(message.voice.file_id)
#             voice_data = BytesIO()
#             await file.download(destination_file=voice_data)
#             text = convert_voice_to_text(voice_data)
#             await update_messages(bot_messages, message.chat.id, "user", text)
#             # await write_log(message.chat.id, f"USER [VOICE] : {text}")
#             db_gpt.add_request(message.chat.id, text)
#             answer = await make_request(bot_messages.get(message.chat.id), message.chat.id)
#             if answer['role'] != 'error':
#                 await update_messages(bot_messages, message.chat.id, answer['role'], answer['content'])
#                 # await write_log(message.chat.id, f"ChatGPT [VOICE] : {answer['content']}")
#                 db_gpt.add_answer(message.chat.id, answer['content'])
#                 if len(answer['content']) > 4095:
#                     await send_long_message(message.chat.id, answer['content'])
#                 else:
#                     await bot.send_message(
#                         chat_id=message.chat.id,
#                         text=answer['content'],
#                         reply_markup=get_main_keyboard()
#                     )
#             else:
#                 await bot.send_message(chat_id=message.chat.id, text=answer['content'])
#         else:
#             await bot.send_message(message.chat.id, text="Вы исчерпали суточный лимит")
#     else:
#         await bot.send_message(message.chat.id, text=BAN_MSG)
    # audio = convert_text_to_voice(answer['content'])
    # await bot.send_voice(chat_id=message.chat.id, voice=audio)


# @dp.message_handler()
# async def handle_text_message(message: types.Message):
#     db_user.check_user(message)
#     if not db_user.check_block(message.chat.id):
#         if db_user.check_limit(message.chat.id):
#             # await write_log(message.chat.id, f"USER [TEXT] : {message.text}")
#             db_gpt.add_request(message.chat.id, message.text)
#             await update_messages(bot_messages, message.chat.id, "user", message.text)
#             answer = await make_request(bot_messages.get(message.chat.id), message.chat.id)
#             if answer['role'] != 'error':
#                 # await write_log(message.chat.id, f"ChatGPT [TEXT] : {answer['content']}")
#                 db_gpt.add_answer(message.chat.id, answer['content'])
#                 await update_messages(bot_messages, message.chat.id, answer['role'], answer['content'])
#                 if len(answer['content']) > 4095:
#                     await send_long_message(message.chat.id, answer['content'])
#                 else:
#                     await bot.send_message(chat_id=message.chat.id, text=answer['content'],
#                                            reply_markup=get_main_keyboard())
#             else:
#                 await bot.send_message(chat_id=message.chat.id, text=answer['content'],
#                                        reply_markup=get_main_keyboard())
#         else:
#             await bot.send_message(message.chat.id, text="Вы исчерпали суточный лимит")
#     else:
#         await bot.send_message(message.chat.id, text=BAN_MSG)


# async def send_long_message(chat_id, message):
#     max_message_size = 4096
#     message_parts = textwrap.wrap(message, max_message_size)
#     for part in message_parts:
#         await bot.send_message(chat_id, part)


if __name__ == '__main__':
    from aiogram import executor

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(on_startup(dp))
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        print(e)
        loop.run_until_complete(on_shutdown(dp))
