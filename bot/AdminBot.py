from aiogram import Router, F, types, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, Message
from django.conf import settings

from bot.db import get_user_language
from bot.keyboards import get_main_menu
from core.settings import ADMIN

from bot.utils import user_languages

dp = Dispatcher()
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# -------------------------------------->   Add Movie   <------------------------------------------- #


# @dp.message(F.text.in_(["️Admin", "️Админ"]))
# async def admin_check(message: Message):
#     user_id = message.from_user.id
#     user_lang = user_languages.get(user_id, 'uz')
#     main_menu_markup = get_main_menu(user_lang)
#     if user_id == ADMIN:
#         await message.answer(get_user_language[user_lang]['admin_welcome'], reply_markup=None)
#     else:
#         await message.answer(get_user_language[user_lang]['admin_not'], reply_markup=main_menu_markup)
#

@dp.message(Command('admin'))
async def admin(message: types.Message):
    user_id = message.from_user.id
    user_lang = user_languages.get(user_id, 'uz')
    main_menu_markup = get_main_menu(user_lang)
    if user_id == ADMIN:
        await message.answer(get_user_language[user_lang]['admin_welcome'], reply_markup=None)
    else:
        await message.answer(get_user_language[user_lang]['admin_not'], reply_markup=main_menu_markup)

