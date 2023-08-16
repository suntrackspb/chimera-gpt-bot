from aiogram import types


def get_gallery_keyboard():
    inline_mark = types.InlineKeyboardMarkup()
    inline_mark.add(types.InlineKeyboardButton(text="Открыть галерею", url="https://sntrk.ru/gallery/"))
    return inline_mark
