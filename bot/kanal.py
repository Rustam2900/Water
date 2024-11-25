from aiogram import Bot
from asgiref.sync import sync_to_async
from django.conf import settings
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.models import CartItem

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


@sync_to_async
def get_cart_items(order):
    return order.cart_items.all()


@sync_to_async
def get_cart_items_from_id(order):
    return list(CartItem.objects.filter(order=order).values_list(
        'product__name',
        'quantity',
        'amount'
    ))


def clean_phone_number(phone_number: str) -> str:
    """
    Telefon raqamidan bo'sh joylarni olib tashlaydi.

    :param phone_number: Raqamli string (masalan, '+998 93 068 29 11')
    :return: Toza telefon raqami (masalan, '+998930682911')
    """
    return phone_number.replace(" ", "")


@sync_to_async
def update_order_total_price(order, total_price):
    order.total_price = total_price
    order.save()


async def send_order_to_channel(
        order,
        full_name,
        phone_number,
        address,
        state,
        county,

):
    channel_id = '-1002256139682'
    cleaned_phone_number = clean_phone_number(phone_number)
    order_message = (
        f"Yangi Buyurtma!\n"
        f"Foydalanuvchi: {full_name}\n"
        f"Telefon raqam: {cleaned_phone_number}\n"
        f"Manzil: {address}\n"
        f"Viloyat: {state}\n"
        f"Tuman: {county}\n"
        f"Buyurtma:\n"
    )

    cart_items = await get_cart_items_from_id(order)

    total_price = 0
    for item in cart_items:
        product_name = item[0]
        quantity = int(item[1])
        total_price_for_item = float(item[2])
        order_message += (
            f"Mahsulot: {product_name}\n"
            f"Miqdor: {quantity}\n"
            f"Narxi: {total_price_for_item} so'm\n"
        )
        total_price += total_price_for_item

    order_message += (
        f"Jami narx: {total_price} so'm\n"
    )

    await bot.send_message(chat_id=channel_id, text=order_message)
