import re
from aiogram import Dispatcher, Bot, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

from bot.keyboards import get_languages, get_main_menu

from bot.utils import default_languages, user_languages, introduction_template, \
    fix_phone
from django.conf import settings
from aiogram.client.default import DefaultBotProperties
from bot.db import save_user_language, save_user_info_to_db, get_user_language, get_my_orders, get_all_product
from bot.states import UserStates
from bot.models import CustomUser

dp = Dispatcher()
bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

phone_number_validator = re.compile(r'^\+998\s?\d{2}\s?\d{3}\s?\d{2}\s?\d{2}$')


@dp.message(CommandStart())
async def welcome(message: Message):
    user_id = message.from_user.id
    user = await CustomUser.objects.filter(telegram_id=user_id).afirst()

    if user and user.user_lang:
        main_menu_markup = get_main_menu(user.user_lang)
        await message.answer(
            text=introduction_template[user.user_lang],
            reply_markup=main_menu_markup
        )
    else:
        msg = default_languages['welcome_message']
        await message.answer(msg, reply_markup=get_languages())


@dp.callback_query(lambda call: call.data.startswith("lang"))
async def get_query_languages(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_lang = call.data.split("_")[1]
    user_languages[user_id] = user_lang

    await save_user_language(user_id, user_lang)

    await bot.answer_callback_query(call.id)
    await state.set_state(UserStates.name)

    text = default_languages[user_lang]['full_name']
    await call.message.answer(text, reply_markup=None)


@dp.message(UserStates.name)
async def reg_user_contact(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_lang = user_languages.get(user_id, 'uz')

    await state.update_data(name=message.text)
    await state.set_state(UserStates.contact)

    text = default_languages.get(user_lang, {}).get('contact', 'Iltimos raqamiz kiriting Namuna: +998 93 068 29 11')
    await message.answer(text)


@dp.message(UserStates.contact)
async def company_contact(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_lang = user_languages.get(user_id, 'uz')

    if message.contact:
        phone = fix_phone(message.contact.phone_number)
    else:
        phone = fix_phone(message.text)

    if not phone_number_validator.match(phone):
        error_message = default_languages[user_lang]['contact']

        await message.answer(error_message)
        return

    await state.update_data(company_contact=phone)

    state_data = await state.get_data()
    user_data = {
        "full_name": state_data.get('name'),
        "phone_number": phone,
        "username": message.from_user.username,
        "user_lang": user_lang,
        "telegram_id": user_id,
        "tg_username": f"https://t.me/{message.from_user.username}",
    }

    try:
        await save_user_info_to_db(user_data)
        success_message = default_languages[user_lang]['successful_registration']
        await message.answer(text=success_message, reply_markup=get_main_menu(user_lang))

    except Exception as e:
        error_message = default_languages[user_lang]['successful_registration']
        await message.answer(text=error_message)

    await state.clear()


@dp.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Созламалар"]))
async def settings(message: Message):
    user_id = message.from_user.id
    user_lang = await get_user_language(user_id)
    await message.answer(text=default_languages[user_lang]['select_language'], reply_markup=get_languages("setLang"))


@dp.callback_query(F.data.startswith("setLang"))
async def change_language(call: CallbackQuery):
    user_id = call.from_user.id
    user_lang = call.data.split("_")[1]
    user_languages[call.from_user.id] = user_lang

    await sync_to_async(update_user_language)(user_id, user_lang)

    await call.message.answer(
        text=default_languages[user_lang]['successful_changed'],
        reply_markup=get_main_menu(user_lang)
    )


def update_user_language(user_id, user_lang):
    try:
        user_language = CustomUser.objects.get(telegram_id=user_id)
        user_language.user_lang = user_lang
        user_language.save()
        print(f"User language updated for {user_id} to {user_lang}")
    except CustomUser.DoesNotExist:
        CustomUser.objects.create(telegram_id=user_id, user_lang=user_lang)
        print(f"User created with language {user_lang} for {user_id}")


@dp.message(F.text.in_(["📦 Mening buyurtmalarim", "📦 Менинг буюртмаларим"]))
async def get_orders(message: Message):
    user_id = message.from_user.id
    user_lang = user_languages.get(user_id, 'uz')

    my_orders = await get_my_orders(user_id)

    if not my_orders:
        await message.answer(
            text=default_languages[user_lang]['order_not_found'],
            reply_markup=get_main_menu(user_lang)
        )
        return

    msg = ""
    sorted_orders = sorted(my_orders, key=lambda order: order.created_at, reverse=True)

    for order in sorted_orders:
        msg = ""
        msg += f"Order #{order.id}\n"
        msg += f"Status: {order.get_status_display()}\n"
        msg += f"Address: {order.address}\n"
        msg += f"Phone: {order.phone_number}\n"
        msg += f"Total Price: {order.total_price} USD\n"
        msg += f"Created At: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        msg += "----------------------------\n"

        await message.answer(text=f"{default_languages[user_lang]['order']}\n{msg}")


@dp.message(F.text.in_(["📲 Biz bilan bog‘lanish", "📲 Биз билан боғланиш"]))
async def contact_us(message: Message):
    user_id = message.from_user.id
    user_lang = user_languages.get(user_id, 'uz')

    contact_info = f"{default_languages[user_lang]['contact_us']}\n" \
                   f"Address: UZB\n" \
                   f"Email: jumanazarustam.com\n" \
                   f"Phone: +998 93 068 29 11\n" \
                   f"Working Hours: Tashkent \n" \
                   f"telegram: @Jumanazarov_Rustam"

    await message.answer(contact_info)


@dp.message(F.text.in_(["Buyurtma berish", "Буюртма бериш"]))
async def get_categories(message: Message):
    user_id = message.from_user.id
    user_lang = await get_user_language(user_id)
    print(f"User language: {user_lang}")
    products = await get_all_product()
    inline_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=[])
    inline_buttons = []

    for product in products:
        if user_lang == 'uz':
            category_name = product.name_uz
        else:
            category_name = product.name_ru
        inline_buttons.append(InlineKeyboardButton(text=category_name, callback_data=f"category_{product.id}"))
    inline_kb.inline_keyboard = [inline_buttons[i:i + 2] for i in range(0, len(inline_buttons), 2)]
    await message.answer(
        text=default_languages[user_lang]['category_select'],
        reply_markup=inline_kb
    )

# @dp.callback_query(lambda call: call.data.startswith("category_"))
# async def handle_products_by_category(call: CallbackQuery):
#     user_id = call.from_user.id
#     user_lang = await get_user_language(user_id)
#     category_id = int(call.data.split("_")[1])
#
#     products = await fetch_products_by_category(category_id)
#     inline_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=[])
#     inline_buttons = []
#
#     for product in products:
#         product_name = product.name_ru if user_lang == 'ru' else product.name_en
#         inline_buttons.append(InlineKeyboardButton(text=product_name, callback_data=f"product_{product.id}"))
#
#     inline_kb.inline_keyboard = [inline_buttons[i:i + 2] for i in range(0, len(inline_buttons), 2)]
#     await call.message.edit_text(text=default_languages[user_lang]['products'], reply_markup=inline_kb)
#
#
# @dp.callback_query(lambda call: call.data.startswith("product_"))
# async def handle_product_detail(call: CallbackQuery):
#     user_id = call.from_user.id
#     product_id = int(call.data.split("_")[1])
#     user_lang = await get_user_language(user_id)
#
#     product = await get_product_detail(product_id)
#
#     product_name = product.name_ru if user_lang == 'ru' else product.name_en
#     description = product.description or "not"
#     message_text = (
#         f"📦 {default_languages[user_lang]['products']}: {product_name}\n\n"
#         f"📄 {default_languages[user_lang]['products_description']}: {description}\n"
#         f"💲 {default_languages[user_lang]['products_price']}: {product.price} USD\n"
#         f"📏 {default_languages[user_lang]['products_size']}: {product.size or 'not'}\n"
#         f"🎨 {default_languages[user_lang]['products_ranks']}: {product.color or 'not'}\n"
#         f"🚚 {default_languages[user_lang]['delivery_time']} {product.delivery_time or 'not'}"
#     )
#
#     inline_kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[])
#     inline_buttons = []
#     inline_buttons.append(
#         InlineKeyboardButton(text=default_languages[user_lang]['place_order'], callback_data=f"order_{product.id}"))
#     inline_kb.inline_keyboard = [inline_buttons[i:i + 2] for i in range(0, len(inline_buttons), 2)]
#
#     await call.message.edit_text(message_text, reply_markup=inline_kb)
#
#
# @dp.callback_query(lambda call: call.data.startswith("order_"))
# async def handle_order_start(call: CallbackQuery, state: FSMContext):
#     user_id = call.from_user.id
#     user_lang = await get_user_language(user_id)
#     product_id = int(call.data.split("_")[1])
#     await call.message.answer(text=default_languages[user_lang]['products_ranks_enter'])
#
#     await state.update_data(product_id=product_id)
#     await state.set_state(OrderState.waiting_for_color)
