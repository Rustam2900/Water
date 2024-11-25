from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    name = State()
    contact = State()


class OrderState(StatesGroup):
    waiting_for_quantity = State()


class OrderAddress(StatesGroup):
    location = State()
    payment = State()
    total_price = State()


class SendMessage(StatesGroup):
    msg = State()


class ProductSave(StatesGroup):
    lotin_name = State()
    kiril_name = State()
    price = State()
    delivery_time = State()


class OrderMinSumState(StatesGroup):
    min_sum = State()


class UserUpdateName(StatesGroup):
    waiting_for_name = State()


class UserUpdatePhone(StatesGroup):
    waiting_for_phone = State()
