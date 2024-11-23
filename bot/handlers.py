import re

from aiogram import Dispatcher, Bot, F
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, \
    ReplyKeyboardMarkup, LabeledPrice, PreCheckoutQuery
from asgiref.sync import sync_to_async

from bot.keyboards import get_languages, get_main_menu

from bot.utils import default_languages, user_languages, introduction_template, \
    fix_phone, message_history
from django.conf import settings
from aiogram.client.default import DefaultBotProperties
from bot.db import save_user_language, save_user_info_to_db, get_user_language, get_my_orders, get_all_product, \
    get_product_detail, get_cart_items, link_cart_items_to_order, add_to_cart, \
    save_order_to_database, get_or_create_order, update_order, get_user, state_get, create_or_update_user_state, \
    create_or_update_user_country, county_get
from bot.states import UserStates, OrderAddress, OrderState
from bot.models import CustomUser
from bot.kanal import send_order_to_channel
from core.settings import PAYMENT_TOKEN, ADMIN

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
            reply_markup=main_menu_markup,
            parse_mode="HTML"
        )
    else:
        msg = default_languages['welcome_message']
        await message.answer(msg, reply_markup=get_languages())

@dp.message(Command('admin'))
async def admin(message: Message):
    user_id = message.from_user.id
    user_lang = user_languages.get(user_id, 'uz')
    main_menu_markup = get_main_menu(user_lang)
    if user_id == 5092869653:
        await message.answer(text="👮🏻‍♂️Admin Xushkelibsiz", reply_markup=None)
    else:
        await message.answer(text="👮🏻‍♂️Uzur siz Admin emassiz", reply_markup=main_menu_markup)

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
async def settings_(message: Message):
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

    contact_info = f"📞+998916694474\n" \
                   f"📩 @Ruqiyasuv \n"
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
        inline_buttons.append(InlineKeyboardButton(text=category_name, callback_data=f"product_{product.id}"))
    inline_kb.inline_keyboard = [inline_buttons[i:i + 2] for i in range(0, len(inline_buttons), 2)]
    await message.answer(
        text=default_languages[user_lang]['category_select'],
        reply_markup=inline_kb
    )


@dp.callback_query(lambda call: call.data.startswith("product_"))
async def handle_product_detail(call: CallbackQuery):
    user_id = call.from_user.id
    product_id = int(call.data.split("_")[1])
    user_lang = await get_user_language(user_id)

    product = await get_product_detail(product_id)

    product_name = product.name_uz if user_lang == 'uz' else product.name_ru
    message_text = (
        f"📦 {default_languages[user_lang]['products']}: {product_name}\n\n"
        f"✅ {default_languages[user_lang]['products_price']}: {product.price} som\n"
        f"🚚 {default_languages[user_lang]['delivery_time']} {product.delivery_time or 'not'}"
    )

    inline_kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[])
    inline_buttons = []
    inline_buttons.append(
        InlineKeyboardButton(text=default_languages[user_lang]['place_order'], callback_data=f"order_{product.id}"))
    inline_buttons.append(
        InlineKeyboardButton(text=default_languages[user_lang]['back'], callback_data="go_back"))
    inline_kb.inline_keyboard = [inline_buttons[i:i + 2] for i in range(0, len(inline_buttons), 2)]

    await call.message.edit_text(message_text, reply_markup=inline_kb)


@dp.callback_query(lambda call: call.data.startswith("order_"))
async def handle_order_start(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_lang = await get_user_language(user_id)
    product_id = int(call.data.split("_")[1])
    await call.message.answer(text=default_languages[user_lang]['products_quantity_enter'])

    await state.update_data(product_id=product_id)
    await state.set_state(OrderState.waiting_for_quantity)


@dp.message(OrderState.waiting_for_quantity)
async def process_quantity(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_lang = await get_user_language(user_id)
    data = await state.get_data()
    quantity = int(message.text)
    print("quantity: ", quantity)
    product_id = data['product_id']

    await add_to_cart(
        user_id=message.from_user.id,
        product_id=product_id,
        quantity=quantity
    )

    await message.answer(default_languages[user_lang]['product_add_cart'])
    await state.clear()


@dp.message(F.text.in_(["🛒Savatcha", "🛒Cаватча"]))
async def show_cart(message: Message):
    user_id = message.from_user.id
    user_lang = await get_user_language(user_id)
    cart_items = await get_cart_items(user_id)

    if not cart_items:
        await message.answer(default_languages[user_lang]['product_not_cart'])
        return

    message_text = f"{default_languages[user_lang]['product_shopping_cart']}\n\n"
    for item in cart_items:
        message_text += (
            f"📦 {item.product.name_uz} - {item.quantity} dona\n"
            f"💲 {default_languages[user_lang]['products_price']} {item.amount} som\n\n"
        )

    inline_kb = InlineKeyboardMarkup(row_width=1, inline_keyboard=[])
    inline_buttons = []
    inline_buttons.append(
        InlineKeyboardButton(text=default_languages[user_lang]['place_order'], callback_data=f"confirm_order"))
    inline_buttons.append(
        InlineKeyboardButton(text=default_languages[user_lang]['back'], callback_data="go_back"))
    inline_kb.inline_keyboard = [inline_buttons[i:i + 2] for i in range(0, len(inline_buttons), 2)]
    await message.answer(message_text, reply_markup=inline_kb)


@dp.callback_query(lambda call: call.data == "go_back")
async def go_back_to_main_menu(call: CallbackQuery):
    user_id = call.from_user.id
    user_lang = await get_user_language(user_id)

    main_menu_keyboard = get_main_menu(user_lang)

    await call.message.edit_reply_markup()
    await call.message.delete()
    await call.message.answer(
        text=introduction_template[user_lang],
        parse_mode="HTML",
        reply_markup=main_menu_keyboard
    )


async def create_location_keyboard(message: Message):
    user_id = message.from_user.id
    user_lang = await get_user_language(user_id)
    if user_lang not in default_languages:
        user_lang = 'uz'
    location_button = KeyboardButton(text=default_languages[user_lang]['send_location'], request_location=True)
    location_keyboard = ReplyKeyboardMarkup(
        keyboard=[[location_button]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return location_keyboard


@dp.callback_query(lambda c: c.data == "confirm_order")
async def request_location(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_lang = await get_user_language(user_id)

    order = await get_or_create_order(user_id)
    is_valid, check_value = await link_cart_items_to_order(user_id, order)

    if not is_valid:
        await callback_query.message.answer(
            text=(
                f"{default_languages[user_lang]['min_order_error']}\n"
                f"{default_languages[user_lang]['min_order_required']}: {check_value}"
            )
        )
        await callback_query.answer()
        return

    states = await state_get()
    inline_kb = InlineKeyboardMarkup(row_width=3, inline_keyboard=[])
    inline_buttons = []

    for state in states:
        state_name = state.name_ru if user_lang == 'ru' else state.name_uz
        inline_buttons.append(
            InlineKeyboardButton(text=state_name or "Bizda faqat hozirda farg'on uchun xizmatarimiz bor",
                                 callback_data=f"state_{state.id}"))

    inline_kb.inline_keyboard = [inline_buttons[i:i + 3] for i in range(0, len(inline_buttons), 3)]
    await callback_query.message.edit_reply_markup(default_languages[user_lang]['state_'], reply_markup=inline_kb)

    await callback_query.answer()


@dp.callback_query(lambda call: call.data.startswith("state_"))
async def handle_products_by_category(call: CallbackQuery):
    user_id = call.from_user.id
    user_lang = await get_user_language(user_id)
    state_id = int(call.data.split("_")[1])

    counties = await county_get(state_id)

    if not counties:
        await call.message.answer(
            text="Bizda faqat hozirda Farg‘ona uchun xizmatlarimiz bor. \n"
                 "Iltimos, boshqa viloyatni tanlang:\n"
                 "Namangadan diller qidirilmoq.\n"
                 "Takliflar uchun:\n"
                 "📞+998916694474 📩 @Ruqiyasuv",
        )
        states = await state_get()
        inline_kb = InlineKeyboardMarkup(row_width=2)
        for state in states:
            state_name = state.name_ru if user_lang == 'ru' else state.name_en
            inline_kb.add(
                InlineKeyboardButton(
                    text=state_name,
                    callback_data=f"state_{state.id}"
                )
            )
        await call.message.answer(
            text=default_languages[user_lang]['select_state'],
            reply_markup=inline_kb
        )
        return

    inline_kb = InlineKeyboardMarkup(row_width=2, inline_keyboard=[])
    inline_buttons = []

    for county in counties:
        country_name = county.name_ru if user_lang == 'ru' else county.name_uz
        inline_buttons.append(
            InlineKeyboardButton(
                text=country_name,
                callback_data=f"country_{county.id}"
            )
        )

    inline_kb.inline_keyboard = [inline_buttons[i:i + 2] for i in range(0, len(inline_buttons), 2)]
    await call.message.edit_reply_markup(reply_markup=inline_kb)
    await create_or_update_user_state(
        telegram_id=user_id,
        state_id=state_id
    )


@dp.callback_query(lambda call: call.data.startswith("country_"))
async def handle_county_selection(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    user_lang = await get_user_language(user_id)

    county_id = int(call.data.split("_")[1])
    user, created = await create_or_update_user_country(
        telegram_id=user_id,
        county_id=county_id
    )
    await call.message.delete()
    await call.message.answer(
        text=default_languages[user_lang]['send_location_order'],
        reply_markup=await create_location_keyboard(call.message)
    )
    await state.set_state(OrderAddress.location)


@dp.message(F.content_type == ContentType.LOCATION)
async def save_location_temp(message: Message, state: FSMContext):
    user_id = message.from_user.id
    latitude = message.location.latitude
    longitude = message.location.longitude
    google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

    await state.update_data(latitude=latitude, longitude=longitude, maps_link=google_maps_link)

    total_price = message_history.pop(user_id, None)
    await state.update_data(total_price=total_price)

    prices = [LabeledPrice(label="Buyurtma narxi", amount=total_price * 100)]
    await bot.send_invoice(
        chat_id=message.from_user.id,
        title="Buyurtma uchun to'lov",
        description="Buyurtma uchun to'lovni amalga oshiring.",
        payload="order_payment_payload",
        provider_token=PAYMENT_TOKEN,
        currency="UZS",
        prices=prices
    )
    await state.set_state(OrderAddress.payment)


@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment_handler(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_lang = await get_user_language(user_id)
    user = await get_user(user_id)

    order_data = await state.get_data()
    latitude = order_data.get("latitude")
    longitude = order_data.get("longitude")
    google_maps_link = order_data.get("maps_link")
    total_price = order_data.get("total_price")

    order = await update_order(
        user_id,
        latitude,
        longitude,
        google_maps_link,
        total_price
    )

    await save_order_to_database(order)
    state_name = user.state.name if user.state else "State not set"
    county_name = user.county.name if user.county else "County not set"

    await send_order_to_channel(
        order,
        user.full_name,
        user.phone_number,
        google_maps_link,
        state_name,
        county_name,
    )
    main_menu_markup = get_main_menu(user_lang)
    await message.answer(text=default_languages[user_lang]['order__'], reply_markup=main_menu_markup)
    await state.clear()



