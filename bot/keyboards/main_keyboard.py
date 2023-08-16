from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard():
    btn_img = KeyboardButton('🎨 Генерация изображения')
    btn_gal = KeyboardButton('🖼 Галерея')
    btn_new = KeyboardButton('📄 Очистить контекст')
    btn_pro = KeyboardButton('⚙️ Профиль')
    main_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    main_markup.row(btn_img)
    main_markup.row(btn_gal)
    main_markup.row(btn_new)
    main_markup.row(btn_pro)
    return main_markup
