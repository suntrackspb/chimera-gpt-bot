from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    MODEL = State()
    COUNT = State()
    STYLE = State()
    DESC = State()
    END = State()
