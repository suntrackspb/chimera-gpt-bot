from aiogram import types


def get_gallery_keyboard():
    inline_mark = types.InlineKeyboardMarkup()
    inline_mark.add(types.InlineKeyboardButton(text="Открыть галерею", url="https://sntrk.ru/gallery/"))
    return inline_mark


def get_models_keyboard():
    style_markup = types.InlineKeyboardMarkup(row_width=2)
    style_markup.add(
        types.InlineKeyboardButton(text="Kandinsky", callback_data="kandinsky-2.2"),
        types.InlineKeyboardButton(text="SDXL", callback_data="sdxl"),
    )
    style_markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel'))
    return style_markup


def get_count_keyboard():
    style_markup = types.InlineKeyboardMarkup()
    style_markup.add(
        types.InlineKeyboardButton(text="1", callback_data="1"),
        types.InlineKeyboardButton(text="2", callback_data="2"),
        types.InlineKeyboardButton(text="3", callback_data="3"),
        types.InlineKeyboardButton(text="4", callback_data="4"),
        types.InlineKeyboardButton(text="5", callback_data="5"),
    )
    style_markup.add(types.InlineKeyboardButton(text='❌ Отмена', callback_data='cancel'))
    return style_markup
