from bot.models import CustomUser, Order, Product
from asgiref.sync import sync_to_async
from django.db import IntegrityError
from decimal import Decimal


@sync_to_async
def sync_save_user_language(user_id, user_lang):
    try:
        user, created = CustomUser.objects.get_or_create(
            telegram_id=user_id,
            defaults={'user_lang': user_lang}
        )

        if not created:
            if user.user_lang != user_lang:
                user.user_lang = user_lang
                user.save()

    except IntegrityError as e:
        print(f"IntegrityError: {e}")


async def save_user_language(user_id, user_lang):
    await sync_save_user_language(user_id, user_lang)


@sync_to_async
def save_user_info_to_db(user_data):
    try:
        new_user, created = CustomUser.objects.update_or_create(
            telegram_id=user_data['telegram_id'],
            defaults={
                "full_name": user_data['full_name'],
                "phone_number": user_data['phone_number'],
                "tg_username": user_data['tg_username'],
                "username": user_data['username']
            }
        )
        return new_user
    except IntegrityError:
        raise Exception("User already exists")


@sync_to_async
def get_my_orders(user_telegram_id):
    try:
        user = CustomUser.objects.get(telegram_id=user_telegram_id)
        orders = Order.objects.filter(user=user)
        return list(orders)
    except CustomUser.DoesNotExist:
        print(f"User with telegram_id {user_telegram_id} not found.")
        return []
    except Exception as e:
        print(f"Error retrieving orders for user {user_telegram_id}: {e}")
        return []


@sync_to_async
def get_all_product():
    return list(
        Product.objects.all()
    )


@sync_to_async
def get_product_by_id(product_id):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None


@sync_to_async
def update_order_item(order_id, product_id, new_quantity):
    order = Order.objects.get(id=order_id)

    for item in order.items:
        if item.get("product_id") == product_id:
            item["quantity"] = new_quantity
            break

    order.calculate_total_price()
    order.save()
    return order


@sync_to_async
def get_user_orders(user_id):
    return Order.objects.filter(user_id=user_id)


@sync_to_async
def get_user_language(user_id):
    try:
        user = CustomUser.objects.get(telegram_id=user_id)
        return user.user_lang
    except CustomUser.DoesNotExist:
        return 'en'


# Function to fetch a product by its ID
@sync_to_async
def get_product_by_id(product_id: int):
    try:
        product = Product.objects.get(id=product_id)
        return product
    except Product.DoesNotExist:
        return None  # Return None if product with the given ID doesn't exist
