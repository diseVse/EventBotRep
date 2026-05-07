from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    choosing_city = State()
    choosing_genre = State()
    choosing_date = State()
    reminder_time = State()
