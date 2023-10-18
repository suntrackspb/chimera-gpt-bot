import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from bot.loader import bot
from bot.keyboards.gallery_keyboard import get_models_keyboard, get_count_keyboard, get_gallery_keyboard
from bot.keyboards.main_keyboard import get_main_keyboard
from bot.keyboards.style_keyboard import get_style_keyboard
from bot.states.states import States
from bot.celery_tasks.generate_img import run_generate_image
from bot.utils.constants import db_user, block, db_img
from bot.utils.msg_templates import BAN_MSG


async def cancel_generation(message: types.Message, state: FSMContext):
    block[message.chat.id] = None
    await state.set_state(States.STYLE.state)
    await state.finish()
    await bot.send_message(message.chat.id, "Генерация изображения отменена", reply_markup=get_main_keyboard())


async def select_model(message: types.Message, state: FSMContext):
    db_user.check_user(message)
    if not db_user.check_block(message.chat.id):
        if block.get(message.chat.id) is None:
            block[message.chat.id] = True
            text = "Выберите модель для генерации изображения: "
            await bot.send_message(message.chat.id, text=text, reply_markup=get_models_keyboard())
            await state.set_state(States.COUNT.state)
        else:
            await bot.send_message(message.chat.id, text="Вы уже генерируете изображение...")
    else:
        await bot.send_message(message.chat.id, text=BAN_MSG)


async def select_count(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'cancel':
        await cancel_generation(query.message, state)
    text = "Выберите количество версий генерации: "
    await state.update_data(model=query.data)
    await bot.edit_message_text(chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                text=text,
                                reply_markup=get_count_keyboard()
                                )
    await state.set_state(States.STYLE.state)


async def select_style(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'cancel':
        await cancel_generation(query.message, state)
    text = "Выберите стиль изображения: "
    await state.update_data(count=query.data)
    await bot.edit_message_text(chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                text=text,
                                reply_markup=get_style_keyboard()
                                )
    await state.set_state(States.DESC.state)


async def enter_prompt(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'cancel':
        await cancel_generation(query.message, state)
    text = "Введите описание изображения: "
    await state.update_data(style=query.data)
    await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
    await bot.send_message(chat_id=query.message.chat.id,
                           text=text,
                           reply_markup=get_main_keyboard()
                           )
    await state.set_state(States.END.state)


async def run_image_generation(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        description = message.text.replace("\n", "").strip()
        answer = "✅ Запрос принят, генерируем изображение... 💤 "
        last_message = await bot.send_message(message.chat.id, text=answer)
        block[message.chat.id] = None
        run_generate_image.delay(
            message.chat.id,
            last_message.message_id,
            data['model'],
            data['count'],
            data['style'],
            description
        )
        await state.finish()
    except Exception as ex:
        print(ex)
    finally:
        block[message.chat.id] = None


async def public_to_gallery(query: types.CallbackQuery):
    filename = query.data
    db_img.update_public(filename)
    await bot.edit_message_text(text='Посмотреть можно тут:',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id, reply_markup=get_gallery_keyboard())


def register_images_handlers(dp: Dispatcher):
    dp.register_message_handler(select_model, commands="img", state="*")
    dp.register_message_handler(select_model, lambda message: message.text == "🎨 Генерация изображения", state="*")
    dp.register_callback_query_handler(select_count, lambda query: query.data, state=States.COUNT)
    dp.register_callback_query_handler(select_style, lambda query: query.data, state=States.STYLE)
    dp.register_callback_query_handler(enter_prompt, lambda query: query.data, state=States.DESC)
    dp.register_message_handler(run_image_generation, state=States.END)
    dp.register_callback_query_handler(public_to_gallery, lambda query: re.match('[0-9_]+', query.data))
