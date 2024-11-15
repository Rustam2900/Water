from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CartItem, Order


@receiver(post_save, sender=CartItem)
@receiver(post_delete, sender=CartItem)
def update_order_total_price(sender, instance, **kwargs):
    if instance.order:
        order = instance.order
        order.total_price = sum(item.amount for item in order.cart_items.all())
        order.save(update_fields=['total_price'])
