# from aiogram import Bot
# from asgiref.sync import sync_to_async
# from django.conf import settings
# from aiogram.client.default import DefaultBotProperties
# from aiogram.enums import ParseMode
#
#
# bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
#
#
# @sync_to_async
# def get_cart_items(order):
#     return order.cart_items.all()
#
#
# @sync_to_async
# def update_order_total_price(order, total_price):
#     order.total_price = total_price
#     order.save()
#
#
# async def send_order_to_channel(order):
#     channel_id = '@IT_RustamDevPythonMy'
#     order_message = (
#         f"Yangi Buyurtma!\n"
#         f"Foydalanuvchi: {order.user.full_name}\n"
#         f"Telefon raqam: {order.user.phone_number}\n"
#         f"Manzil: {order.address}\n\n"
#         f"Buyurtma:\n"
#     )
#
#     cart_items = await get_cart_items(order)
#
#     total_price = 0
#     for item in cart_items:
#         product_name = item.product.name
#         quantity = item.quantity
#         total_price_for_item = item.amount
#         order_message += (
#             f"Mahsulot: {product_name}\n"
#             f"Miqdor: {quantity}\n"
#             f"Narxi: {total_price_for_item} so'm\n\n"
#         )
#         total_price += total_price_for_item
#
#     order_message += (
#         f"Jami narx: {total_price} so'm\n"
#         f"Google Maps manzili: {order.address}\n"
#     )
#
#     await update_order_total_price(order, total_price)
#
#     await bot.send_message(chat_id=channel_id, text=order_message)
#
#     image_path = f"media/{order.receipt_image.name}"
#     with open(image_path, "rb") as image_che:
#         await bot.send_photo(channel_id, image_che)
