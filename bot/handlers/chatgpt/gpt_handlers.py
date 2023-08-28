import textwrap
from io import BytesIO

from aiogram import types, Dispatcher

from bot.keyboards.main_keyboard import get_main_keyboard
from bot.main import bot
from bot.utils.chimera_api import make_request
from bot.utils.constants import bot_messages, db_user, db_gpt
from bot.utils.converters import convert_voice_to_text
from bot.utils.msg_templates import BAN_MSG, LIMIT_MSG


async def update_messages(msg, uid, role, content):
    if msg.get(uid) is None:
        msg[uid] = [{'role': role, 'content': content}]
    else:
        if len(msg.get(uid)) >= 10:
            if msg[uid][0]['role'] == 'system':
                msg[uid].pop(1)
            else:
                msg[uid].pop(0)
        msg[uid].append({'role': role, 'content': content})


async def add_context(message: types.Message):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        text = message.text.removeprefix('/add ')
        if text != '/add':
            bot_messages[message.chat.id] = []
            await update_messages(bot_messages, message.chat.id, "system", text)
            await message.answer(f"Установлен system context {text}", reply_markup=get_main_keyboard())
            db_gpt.add_request(message.chat.id, f"SYSTEM: {text}")
            db_gpt.add_request(message.chat.id, text)
        else:
            await message.answer(text=f"Необходимо указать как бот должен себя вести \n"
                                      f"Например: _/add Действуй как юрист._")
    else:
        await bot.send_message(message.chat.id, text=BAN_MSG)


async def handle_voice_message(message: types.Message):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        if db_user.check_limit(message.chat.id):
            file = await bot.get_file(message.voice.file_id)
            voice_data = BytesIO()
            await file.download(destination_file=voice_data)
            text = convert_voice_to_text(voice_data)
            await update_messages(bot_messages, message.chat.id, "user", text)
            # await write_log(message.chat.id, f"USER [VOICE] : {text}")
            db_gpt.add_request(message.chat.id, text)
            answer = await make_request(bot_messages.get(message.chat.id), message.chat.id)
            if answer['role'] != 'error':
                await update_messages(bot_messages, message.chat.id, answer['role'], answer['content'])
                # await write_log(message.chat.id, f"ChatGPT [VOICE] : {answer['content']}")
                db_gpt.add_answer(message.chat.id, answer['content'])
                if len(answer['content']) > 4095:
                    await send_long_message(message.chat.id, answer['content'])
                else:
                    await bot.send_message(
                        chat_id=message.chat.id,
                        text=answer['content'],
                        reply_markup=get_main_keyboard()
                    )
            else:
                await bot.send_message(chat_id=message.chat.id, text=answer['content'])
        else:
            await bot.send_message(message.chat.id, text=LIMIT_MSG)
    else:
        await bot.send_message(message.chat.id, text=BAN_MSG)
    # audio = convert_text_to_voice(answer['content'])
    # await bot.send_voice(chat_id=message.chat.id, voice=audio)


async def handle_text_message(message: types.Message):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        if db_user.check_limit(message.chat.id):
            # await write_log(message.chat.id, f"USER [TEXT] : {message.text}")
            db_gpt.add_request(message.chat.id, message.text)
            await update_messages(bot_messages, message.chat.id, "user", message.text)
            answer = await make_request(bot_messages.get(message.chat.id), message.chat.id)
            if answer['role'] != 'error':
                # await write_log(message.chat.id, f"ChatGPT [TEXT] : {answer['content']}")
                db_gpt.add_answer(message.chat.id, answer['content'])
                await update_messages(bot_messages, message.chat.id, answer['role'], answer['content'])
                if len(answer['content']) > 4095:
                    await send_long_message(message.chat.id, answer['content'])
                else:
                    await bot.send_message(chat_id=message.chat.id, text=answer['content'],
                                           reply_markup=get_main_keyboard())
            else:
                await bot.send_message(chat_id=message.chat.id, text=answer['content'],
                                       reply_markup=get_main_keyboard())
        else:
            await bot.send_message(message.chat.id, text=LIMIT_MSG)
    else:
        await bot.send_message(message.chat.id, text=BAN_MSG)


async def send_long_message(chat_id, message):
    max_message_size = 4096
    message_parts = textwrap.wrap(message, max_message_size)
    for part in message_parts:
        await bot.send_message(chat_id, part)


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(add_context, commands="add")
    dp.register_message_handler(handle_voice_message, content_types=types.ContentType.VOICE)
    dp.register_message_handler(handle_text_message, content_types=types.ContentType.TEXT)
