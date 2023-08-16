from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):

    STYLE = State()  # Initial state

    DESC = State()  # State for asking the user's name

    END = State()  # Final state
