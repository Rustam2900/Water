from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.db import get_statistics, get_all_users, get_all_product
from bot.keyboards import get_main_menu, get_admin_menu
from bot.models import Product
from core.settings import ADMIN
from bot.utils import user_languages
from bot.states import SendMessage, ProductSave

from aiogram.utils.text_decorations import html_decoration as fmt

router = Router()
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# -------------------------------------->   Add Movie   <------------------------------------------- #
print("###############", ADMIN)


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


@router.message(F.text == "👤Statistika")
async def show_statistics(message: Message):
    user_id = message.from_user.id
    if user_id == 5092869653:
        statistics = await get_statistics()
        await message.answer(text=statistics)
    else:
        await message.answer(text="Siz admin emassiz, statistikani ko'rish huquqiga ega emassiz.", reply_markup=None)


@router.message(F.text == "✍️ Habar yuborish")
async def send_message_users(message: Message, state: FSMContext):
    if message.from_user.id == 5092869653:
        await state.set_state(SendMessage.msg)
        await message.answer(text='Reklama xabarini yuboring!', reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer('Sizga bu buyruqdan foydalana olmaysiz')


@router.message(SendMessage.msg)
async def send_message(message: Message, state: FSMContext):
    await state.clear()
    users = await get_all_users()
    total_users = len(users)
    failed_count = 0

    for user in users:
        try:
            await bot.forward_message(
                chat_id=user.telegram_id,
                from_chat_id=message.from_user.id,
                message_id=message.message_id,
            )
        except Exception:
            failed_count += 1

    sent_count = total_users - failed_count
    await bot.send_message(
        chat_id=5092869653,
        text=(
            f"<b>Bot a'zolari soni:</b> {total_users}\n"
            f"<b>Yuborilmadi:</b> {failed_count}\n"
            f"<b>Yuborildi:</b> {sent_count}"
        ),
        parse_mode=ParseMode.HTML,
    )


@router.message(F.text == "➕ Mahsulot qo'shish")
async def add_product(message: Message, state: FSMContext):
    if message.from_user.id == 5092869653:
        await state.set_state(ProductSave.lotin_name)
        await message.answer("Mahsulot nomini kiriting lotin tilida \n"
                             "Namuna: 20 L suv:")
    else:
        await message.answer("Siz admin emassiz, mahsulot qo'shish huquqiga ega emassiz:", reply_markup=None)


@router.message(ProductSave.lotin_name)
async def add_name_uz(message: Message, state: FSMContext):
    if message.from_user.id == 5092869653:
        await state.update_data(lotin_name=message.text)
        await state.set_state(ProductSave.kiril_name)
        await message.answer("Mahsulor nomini kiriting Kiril harfida \n"
                             "Namuna 20 Л сув")
    else:
        await message.answer("Siz admin emassiz, mahsulot qo'shish huquqiga ega emassiz:", reply_parameters=None)


def is_valid_kiril_text(text: str) -> bool:
    import re
    return bool(re.match(r'^[\u0400-\u04FF\s\d]+$', text.strip()))


@router.message(ProductSave.kiril_name)
async def add_name_ru(message: Message, state: FSMContext):
    if message.from_user.id == 5092869653:
        if is_valid_kiril_text(message.text):
            await state.update_data(kiril_name=message.text)
            await state.set_state(ProductSave.price)
            await message.answer("Mahsulot narxini kiriting.\n"
                                 "Namuna: 15000")
        else:
            await message.answer("Iltimos, Kiril harflarida va raqamlar bilan yozing.\n"
                                 "Namuna: 20 Л сув")
    else:
        await message.answer("Siz admin emassiz, mahsulot qo'shish huquqiga ega emassiz")


@router.message(ProductSave.price)
async def add_price(message: Message, state: FSMContext):
    if message.text.isdigit():
        price = int(message.text)
        await state.update_data(price=price)
        await state.set_state(ProductSave.delivery_time)
        await message.answer("Yetkazib berish vaqtini kiriting.\n"
                             "Namuna: Bepul yoki 1-3 soat")
    else:
        await message.answer("Iltimos, faqat raqam kiriting.\n"
                             "Namuna: 15000")


@router.message(ProductSave.delivery_time)
async def add_delivery_time(message: Message, state: FSMContext):
    delivery_time = message.text.strip()
    await state.update_data(delivery_time=delivery_time)
    data = await state.get_data()

    await sync_to_async(Product.objects.create)(
        name_uz=data['lotin_name'],
        name_ru=data['kiril_name'],
        price=data['price'],
        delivery_time=data['delivery_time']
    )

    await message.answer(fmt.bold("Mahsulot muvaffaqiyatli qo'shildi!"),
                         parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
    await state.clear()


async def get_product_keyboard(user_lang):
    products = await get_all_product()
    inline_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=[])
    inline_buttons = []

    for product in products:
        category_name = (
            product.name_uz if user_lang == "uz" else product.name_ru
        )
        inline_buttons.append(
            InlineKeyboardButton(
                text=f"{category_name} ({product.price} so'm)",
                callback_data=f"delete_{product.id}",
            )
        )

    inline_kb.inline_keyboard = [
        inline_buttons[i: i + 2] for i in range(0, len(inline_buttons), 2)
    ]
    return inline_kb


@router.message(F.text == "➖ Mahsulot o'chirish")
async def remove_product(message: Message):
    if message.from_user.id == 5092869653:
        user_lang = "uz"
        keyboard = await get_product_keyboard(user_lang)
        if keyboard.inline_keyboard:
            await message.answer(
                text="O'chiriladigan mahsulotni tanlang:",
                reply_markup=keyboard,
            )
        else:
            await message.answer("Hozircha mahsulot mavjud emas.")
    else:
        await message.answer(
            "Siz admin emassiz, mahsulot o'chirish huquqiga ega emassiz."
        )


@router.callback_query(lambda c: c.data.startswith("delete_"))
async def confirm_delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    try:
        product = await sync_to_async(Product.objects.get)(id=product_id)
        await sync_to_async(product.delete)()
        await callback.message.edit_text(
            f"Mahsulot '{product.name}' muvaffaqiyatli o'chirildi!"
        )
    except Product.DoesNotExist:
        await callback.message.edit_text(
            "Tanlangan mahsulot topilmadi yoki allaqachon o'chirilgan."
        )
