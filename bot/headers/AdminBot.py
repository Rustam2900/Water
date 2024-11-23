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

router = Router()
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# -------------------------------------->   Add Movie   <------------------------------------------- #


@router.message(Command('admin'))
async def admin(message: Message):
    user_id = message.from_user.id
    user_lang = user_languages.get(user_id, 'uz')
    main_menu_markup = get_main_menu(user_lang)
    if user_id == 5092869653:
        await message.answer(text="👮🏻‍♂️Admin Xushkelibsiz", reply_markup=None)
    else:
        await message.answer(text="👮🏻‍♂️Uzur siz Admin emassiz", reply_markup=main_menu_markup)
