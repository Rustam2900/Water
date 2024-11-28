from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.db import get_all_users, get_all_product, get_all_blocked_users, get_user_statistics, \
    get_product_statistics
from bot.keyboards import get_main_menu, get_admin_menu
from bot.models import Product, OrderMinSum, CustomUser, BlockedUser
from bot.utils import user_languages, default_languages
from bot.states import SendMessage, ProductSave, OrderMinSumState

from aiogram.utils.text_decorations import html_decoration as fmt

router = Router()
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# -------------------------------------->   Add Movie   <------------------------------------------- #


@router.message(Command('admin'))
async def admin(message: Message):
    user_id = message.from_user.id
    user_lang = user_languages.get(user_id, 'uz')
    is_blocked = await sync_to_async(BlockedUser.objects.filter(telegram_id=user_id).exists)()

    if is_blocked:
        await message.answer(
            default_languages[user_lang]['not']
        )
        return

    user = await CustomUser.objects.filter(telegram_id=user_id).afirst()
    main_menu_markup = get_main_menu(user_lang)
    admin_menu_markup = get_admin_menu(user_lang)
    if user_id == 6736873215:
        await message.answer(text="👮🏻‍♂️Admin Xushkelibsiz\n"
                                  "Iltimos, quyidagi buyruqlardan birini tanlang:", reply_markup=admin_menu_markup)
    else:
        await message.answer(text="👮🏻‍♂️Uzur siz Admin emassiz", reply_markup=main_menu_markup)


@router.message(F.text == "👤Statistika")
async def show_statistics(message: Message):
    user_id = message.from_user.id
    if user_id == 6736873215:
        user_stats = await get_user_statistics()
        product_stats = await get_product_statistics()

        statistics = f"👤 Foydalanuvchilar:\n" \
                     f"24 soatda yangi foydalanuvchilar: {user_stats['new_users_24h']}\n" \
                     f"1 oyda yangi foydalanuvchilar: {user_stats['new_users_1_month']}\n" \
                     f"Jami foydalanuvchilar: {user_stats['total_users']}\n\n"

        statistics += "📦 Mahsulot statistikasi (24 soat):\n"
        if product_stats["stats_24h"]:
            for stat in product_stats["stats_24h"]:
                statistics += f"{stat['product__name']}: {stat['total_quantity']} dona sotilgan\n"
        else:
            statistics += "No data available for the last 24 hours.\n"

        statistics += "\n📦 Mahsulot statistikasi (1 oy):\n"
        if product_stats["stats_1_month"]:
            for stat in product_stats["stats_1_month"]:
                statistics += f"{stat['product__name']}: {stat['total_quantity']} dona sotilgan\n"
        else:
            statistics += "No data available for the last month.\n"

        statistics += "\n📦 Mahsulot statistikasi (Jami):\n"
        if product_stats["total_stats"]:
            for stat in product_stats["total_stats"]:
                statistics += f"{stat['product__name']}: {stat['total_quantity']} dona sotilgan\n"
        else:
            statistics += "No total product data available.\n"

        await message.answer(text=statistics)
    else:
        await message.answer(
            text="Siz admin emassiz, statistikani ko'rish huquqiga ega emassiz.",
            reply_markup=None
        )


@router.message(F.text == "✍️ Habar yuborish")
async def send_message_users(message: Message, state: FSMContext):
    if message.from_user.id == 6736873215:
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
        chat_id=6736873215,
        text=(
            f"<b>Bot a'zolari soni:</b> {total_users}\n"
            f"<b>Yuborilmadi:</b> {failed_count}\n"
            f"<b>Yuborildi:</b> {sent_count}"
        ),
        parse_mode=ParseMode.HTML,
    )


@router.message(F.text == "➕ Mahsulot qo'shish")
async def add_product(message: Message, state: FSMContext):
    if message.from_user.id == 6736873215:
        await state.set_state(ProductSave.lotin_name)
        await message.answer("Mahsulot nomini kiriting lotin tilida \n"
                             "Namuna: 20 L suv:")
    else:
        await message.answer("Siz admin emassiz, mahsulot qo'shish huquqiga ega emassiz:", reply_markup=None)


@router.message(F.text == "💸 Min Summa")
async def add_min_sum(message: Message, state: FSMContext):
    if message.from_user.id == 6736873215:
        await state.set_state(OrderMinSumState.min_sum)
        await message.answer("Iltimos Minimal miqdor kiriting \n"
                             "Namuna: 15000")
    else:
        await message.answer("Siz admin emassiz, mahsulot qo'shish huquqiga ega emassiz:", reply_markup=None)


@router.message(OrderMinSumState.min_sum)
async def add_min_sum_admin_save(message: Message, state: FSMContext):
    if message.text.isdigit():
        min_sum = int(message.text)
        await state.update_data(min_sum=min_sum)

        existing_record = await sync_to_async(OrderMinSum.objects.first)()

        if existing_record:
            existing_record.min_order_sum = min_sum
            await sync_to_async(existing_record.save)()
        else:
            await sync_to_async(OrderMinSum.objects.create)(
                min_order_sum=min_sum
            )

        await message.answer(
            fmt.bold("Miqdor muvaffaqiyatli saqlandi!"),
            parse_mode='HTML',
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()


@router.message(ProductSave.lotin_name)
async def add_name_uz(message: Message, state: FSMContext):
    if message.from_user.id == 6736873215:
        await state.update_data(lotin_name=message.text)
        await state.set_state(ProductSave.kiril_name)
        await message.answer("Mahsulor nomini kiriting Kiril harfida \n"
                             "Namuna 20 Л сув")
    else:
        await message.answer("Siz admin emassiz, mahsulot qo'shish huquqiga ega emassiz:", reply_parameters=None)


def is_valid_kiril_text(text: str) -> bool:
    import re
    return bool(re.match(r'^[\u0400-\u04FF\s\d.]+$', text.strip()))


@router.message(ProductSave.kiril_name)
async def add_name_ru(message: Message, state: FSMContext):
    if message.from_user.id == 6736873215:
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
        await state.set_state(ProductSave.delivery_time_lotin)
        await message.answer("Yetkazib berish vaqtini lotin harflarida kiriting.\n"
                             "Namuna: Bepul yoki 1-3 soat")
    else:
        await message.answer("Iltimos, faqat raqam kiriting.\n"
                             "Namuna: 15000")


@router.message(ProductSave.delivery_time_lotin)
async def add_delivery_time_lotin(message: Message, state: FSMContext):
    delivery_time_lotin = message.text.strip()
    await state.update_data(delivery_time_lotin=delivery_time_lotin)
    await state.set_state(ProductSave.delivery_time_kiril)
    await message.answer("Yetkazib berish vaqtini kiril harflarida kiriting.\n"
                         "Namuna: Бепул")


@router.message(ProductSave.delivery_time_kiril)
async def add_delivery_time_kiril(message: Message, state: FSMContext):
    if is_valid_kiril_text(message.text):
        delivery_time_kiril = message.text.strip()
        await state.update_data(delivery_time_kiril=delivery_time_kiril)
        data = await state.get_data()

        await sync_to_async(Product.objects.create)(
            name_uz=data['lotin_name'],
            name_ru=data['kiril_name'],
            price=data['price'],
            delivery_time_uz=data['delivery_time_lotin'],
            delivery_time_ru=data['delivery_time_kiril']
        )

        await message.answer(fmt.bold("Mahsulot muvaffaqiyatli qo'shildi!"),
                             parse_mode='HTML', reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer("Iltimos, Kiril harflarida va raqamlar bilan yozing.\n"
                             "Namuna: Бепул")


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
    if message.from_user.id == 6736873215:
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


async def get_user_keyboard():
    users = await get_all_users()
    inline_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=[])
    inline_buttons = []

    for user in users:
        inline_buttons.append(
            InlineKeyboardButton(
                text=f"{user.full_name or user.username} ({user.telegram_id})",
                callback_data=f"block_{user.id}",
            )
        )

    inline_kb.inline_keyboard = [
        inline_buttons[i: i + 2] for i in range(0, len(inline_buttons), 2)
    ]
    return inline_kb


@router.callback_query(lambda c: c.data.startswith("block_"))
async def block_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    try:
        user = await sync_to_async(CustomUser.objects.get)(id=user_id)
        blocked_user, created = await sync_to_async(BlockedUser.objects.get_or_create)(
            telegram_id=user.telegram_id,
            defaults={
                "full_name": user.full_name,
                "username": user.username,
                "phone_number": user.phone_number,
            },
        )
        if created:
            await callback.message.edit_text(
                f"Foydalanuvchi '{user.full_name or user.username}' muvaffaqiyatli bloklandi!"
            )
        else:
            await callback.message.edit_text("Bu foydalanuvchi allaqachon qora ro'yxatda mavjud.")
    except CustomUser.DoesNotExist:
        await callback.message.edit_text("Tanlangan foydalanuvchi topilmadi.")


@router.message(F.text == "🚫 Foydalanuvchini bloklash")
async def show_users_to_block(message: Message):
    if message.from_user.id == 6736873215:
        keyboard = await get_user_keyboard()
        if keyboard.inline_keyboard:
            await message.answer(
                text="Bloklanadigan foydalanuvchini tanlang:",
                reply_markup=keyboard,
            )
        else:
            await message.answer("Hozircha ro'yxatda foydalanuvchilar yo'q.")
    else:
        await message.answer("Siz admin emassiz, foydalanuvchilarni bloklash huquqiga ega emassiz.")


async def get_unblock_keyboard():
    blocked_users = await get_all_blocked_users()
    inline_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=[])
    inline_buttons = []

    for user in blocked_users:
        inline_buttons.append(
            InlineKeyboardButton(
                text=f"{user.full_name or user.username} ({user.telegram_id})",
                callback_data=f"unblock_{user.id}",
            )
        )

    inline_kb.inline_keyboard = [
        inline_buttons[i: i + 2] for i in range(0, len(inline_buttons), 2)
    ]
    return inline_kb


@router.callback_query(lambda c: c.data.startswith("unblock_"))
async def unblock_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])

    try:
        user = await sync_to_async(BlockedUser.objects.get)(id=user_id)
        await sync_to_async(user.delete)()
        await callback.message.edit_text(
            f"Foydalanuvchi '{user.full_name or user.username}' muvaffaqiyatli blokdan chiqarildi!"
        )
    except BlockedUser.DoesNotExist:
        await callback.message.edit_text("Tanlangan foydalanuvchi topilmadi yoki allaqachon blokdan chiqarilgan.")


@router.message(F.text == "🚫 Foydalanuvchini blokdan ochish")
async def show_blocked_users(message: Message):
    if message.from_user.id == 6736873215:
        keyboard = await get_unblock_keyboard()
        if keyboard.inline_keyboard:
            await message.answer(
                text="Blokdan ochiladigan foydalanuvchini tanlang:",
                reply_markup=keyboard,
            )
        else:
            await message.answer("Bloklangan foydalanuvchilar ro'yxati bo'sh.")
    else:
        await message.answer("❌ Siz bu komandani bajarish huquqiga ega emassiz.")
