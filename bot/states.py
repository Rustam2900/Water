from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    name = State()
    contact = State()
