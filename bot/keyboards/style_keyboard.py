from aiogram import types


def get_style_keyboard():
    style_markup = types.InlineKeyboardMarkup(row_width=2)
    style_markup.add(
        types.InlineKeyboardButton(text='Без стиля', callback_data='DEFAULT'),
        types.InlineKeyboardButton(text='Anime', callback_data='ANIME'),
        types.InlineKeyboardButton(text='Cyberpunk', callback_data='CYBERPUNK'),
        types.InlineKeyboardButton(text='Digital Art', callback_data='DIGITALPAINTING'),
        types.InlineKeyboardButton(text='Детальное фото', callback_data='UHD'),
        types.InlineKeyboardButton(text='Студийное фото', callback_data='STUDIOPHOTO'),
        types.InlineKeyboardButton(text='Портретное фото', callback_data='PORTRAITPHOTO'),
        types.InlineKeyboardButton(text='Средневековье', callback_data='MEDIEVALPAINTING'),
        types.InlineKeyboardButton(text='Рисунок карандашом', callback_data='PENCILDRAWING'),
        types.InlineKeyboardButton(text='Картина маслом', callback_data='OILPAINTING'),
        types.InlineKeyboardButton(text='3D Рендер', callback_data='RENDER'),
        types.InlineKeyboardButton(text='Мультфильм', callback_data='CARTOON'),
    )
    style_markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel'))
    return style_markup
