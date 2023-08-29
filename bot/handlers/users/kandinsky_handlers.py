import re

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from bot.keyboards.gallery_keyboard import get_gallery_keyboard
from bot.keyboards.main_keyboard import get_main_keyboard
from bot.keyboards.style_keyboard import get_style_keyboard
from bot.loader import bot
from bot.states.states import States
from bot.utils.constants import db_user, block, db_img
from bot.utils.kandinsky_api import generate_image
from bot.utils.msg_templates import BAN_MSG, styles


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


async def public_to_gallery(query: types.CallbackQuery):
    filename = query.data
    db_img.update_public(filename)
    await bot.edit_message_text(text='Посмотреть можно тут:',
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id, reply_markup=get_gallery_keyboard())


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


def register_kandinsky_handlers(dp: Dispatcher):
    dp.register_message_handler(create_image, commands="img")
    dp.register_message_handler(create_image, lambda message: message.text == "🎨 Генерация изображения")

    dp.register_callback_query_handler(public_to_gallery, lambda query: re.match('[0-9_]+', query.data))
    dp.register_callback_query_handler(allow_profile, lambda query: query.data)

    dp.register_message_handler(enter_prompt, state=States.STYLE)
