from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from django.conf import settings

from bot.db import get_statistics, get_all_users
from bot.keyboards import get_main_menu, get_admin_menu
from core.settings import ADMIN
from bot.utils import user_languages
from bot.states import SendMessage

router = Router()
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# -------------------------------------->   Add Movie   <------------------------------------------- #


@router.message(Command('admin'))
async def admin(message: Message):
    user_id = message.from_user.id
    user_lang = user_languages.get(user_id, 'uz')
    main_menu_markup = get_main_menu(user_lang)
    admin_menu_markup = get_admin_menu(user_lang)
    if user_id == 5092869653:
        await message.answer(text="👮🏻‍♂️Admin Xushkelibsiz\n"
                                  "Iltimos, quyidagi buyruqlardan birini tanlang:", reply_markup=admin_menu_markup)
    else:
        await message.answer(text="👮🏻‍♂️Uzur siz Admin emassiz", reply_markup=main_menu_markup)


@router.message(F.text == "Statistika")
async def show_statistics(message: Message):
    user_id = message.from_user.id
    if user_id == 5092869653:
        statistics = await get_statistics()
        await message.answer(text=statistics)
    else:
        await message.answer(text="Siz admin emassiz, statistikani ko'rish huquqiga ega emassiz.", reply_markup=None)


@router.message(F.text == "Habar yuborish")
async def send_message_users(message: Message, state: FSMContext):
    if message.from_user.id == 5092869653:
        await state.set_state(SendMessage.msg)
        await message.answer(text='Reklama xabarini yuboring!', reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer('Sizga bu buyruqdan foydalana olmaysiz')


@router.message(SendMessage.msg)
async def send_message(message: Message, state: FSMContext):
    count = 0
    await state.clear()
    users = await get_all_users()
    for i in users:
        try:
            await bot.forward_message(chat_id=i.user_id, from_chat_id=message.from_user.id,
                                      message_id=message.message_id)
        except Exception:
            count += 1
    await bot.send_message(chat_id=5092869653,
                           text=f'<b>Bot azolari - {len(users)}\n\nYuborilmadi - {count}\n\nYuborildi - {len(users) - count}</b>',
                           parse_mode=ParseMode.HTML)


@router.message(F.text == "Mahsulot qo'shish")
async def add_product(message: Message):
    if message.from_user.id == 5092869653:
        await message.answer("Mahsulot qo'shish funksiyasi ishga tushdi.")
    else:
        await message.answer("Siz admin emassiz, mahsulot qo'shish huquqiga ega emassiz.", reply_markup=None)


@router.message(F.text == "Mahsulot o'chirish")
async def remove_product(message: Message):
    if message.from_user.id == 5092869653:
        await message.answer("Mahsulot o'chirish funksiyasi ishga tushdi.")
    else:
        await message.answer("Siz admin emassiz, mahsulot o'chirish huquqiga ega emassiz.", reply_markup=None)
