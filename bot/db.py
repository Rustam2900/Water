from asgiref.sync import sync_to_async
from django.db import IntegrityError

from bot.models import CustomUser, Order, Product, CartItem, OrderMinSum, State, County
from bot.utils import message_history


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
def get_user_orders(user_id):
    return Order.objects.filter(user_id=user_id)


@sync_to_async
def get_user(user_id):
    return CustomUser.objects.select_related('state', 'county').get(telegram_id=user_id)


@sync_to_async
def get_user_language(user_id):
    try:
        user = CustomUser.objects.get(telegram_id=user_id)
        return user.user_lang
    except CustomUser.DoesNotExist:
        return 'uz'


@sync_to_async
def get_product_detail(product_id):
    return Product.objects.get(id=product_id)


@sync_to_async
def get_cart_items(user_id):
    return list(CartItem.objects.filter(user__telegram_id=user_id, order__isnull=True).select_related('product'))


@sync_to_async
def link_cart_items_to_order(user_id, order):
    cart_items = CartItem.objects.filter(user__telegram_id=user_id, order__isnull=True)
    total_price = sum(item.amount for item in cart_items)

    for item in cart_items:
        item.order = order

    order.total_price = total_price


@sync_to_async
def get_or_create_order(
        user_id,
        latitude=None,
        longitude=None,
        google_maps_link=None,
        total_price=None
):
    user = CustomUser.objects.get(telegram_id=user_id)

    orders = Order.objects.filter(
        user=user,
        status=Order.OrderStatus.CREATED,
    ).exclude(id__in=[order.id for order in Order.objects.filter(user=user)])

    if orders.exists():
        order = orders.first()
    else:
        order = Order.objects.create(
            user=user,
            status=Order.OrderStatus.CREATED,
            address=google_maps_link,
            latitude=latitude,
            longitude=longitude,
            total_price=total_price,
            phone_number=user.phone_number,
        )
    return order


@sync_to_async
def update_order(
        user_id,
        latitude=None,
        longitude=None,
        google_maps_link=None,
        total_price=None
):
    user = CustomUser.objects.get(telegram_id=user_id)

    order = Order.objects.filter(
        user=user,
        status=Order.OrderStatus.CREATED,
    ).last()

    if not order:
        raise ValueError("No existing order with status 'CREATED' found.")

    order.status = Order.OrderStatus.PAYED
    order.address = google_maps_link
    order.latitude = latitude
    order.longitude = longitude
    order.total_price = total_price
    order.phone_number = user.phone_number
    order.save()

    return order


@sync_to_async
def add_to_cart(user_id, product_id, quantity):
    product = Product.objects.get(id=product_id)
    user = CustomUser.objects.get(telegram_id=user_id)
    amount = product.price * quantity

    CartItem.objects.create(
        user=user,
        product=product,
        quantity=quantity,
        amount=amount
    )


@sync_to_async(thread_sensitive=True)
def save_order_to_database(order):
    try:
        CartItem.objects.filter(order=order).update(order=order)
    except Exception as e:
        print(f"Error saving order to database: {e}")


@sync_to_async
def link_cart_items_to_order(user_id, order):
    cart_items = CartItem.objects.filter(user__telegram_id=user_id, order__isnull=True)

    if not cart_items:
        return False, None

    total_price = sum(item.amount for item in cart_items)

    min_order_sum = OrderMinSum.objects.first()
    if min_order_sum and total_price < float(min_order_sum.min_order_sum):
        return False, float(min_order_sum.min_order_sum)

    cart_items.update(order=order)
    updated_cart_items = CartItem.objects.filter(user__telegram_id=user_id, order=order)
    print(f"Updated cart items: {list(updated_cart_items)}")

    order.total_price = total_price
    message_history[user_id] = total_price
    order.save()
    print(f"Order saved with total_price: {order.total_price}")

    return True, total_price


@sync_to_async
def state_get():
    return list(State.objects.all())


@sync_to_async
def county_get(state_id):
    return list(County.objects.filter(state_id=state_id))


@sync_to_async
def create_or_update_user_state(telegram_id, state_id):
    try:
        state_instance = State.objects.get(id=state_id)

        user, created = CustomUser.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                'state': state_instance
            }
        )
        return user, created
    except (IntegrityError, State.DoesNotExist) as e:
        return None, False


@sync_to_async
def create_or_update_user_country(telegram_id, county_id):
    try:
        county_instance = County.objects.get(id=county_id)

        state_instance = county_instance.state

        user, created = CustomUser.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                'state': state_instance,
                'county': county_instance,
            }
        )
        return user, created
    except (IntegrityError, County.DoesNotExist) as e:
        return None, False
