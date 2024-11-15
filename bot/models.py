from django.db import models
from django.utils.translation import gettext_lazy as _
from bot.validators import phone_number_validator


class CustomUser(models.Model):
    full_name = models.CharField(_("full name"), blank=True, max_length=255)
    username = models.CharField(_("username"), blank=True, max_length=255, null=True)
    phone_number = models.CharField(blank=True, unique=True, validators=[phone_number_validator],
                                    max_length=20)
    user_lang = models.CharField(blank=True, null=True, max_length=10)
    telegram_id = models.CharField(blank=True, null=True, max_length=255, unique=True)
    tg_username = models.CharField(_("telegram username"), blank=True, null=True, max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.full_name


class Product(models.Model):
    name = models.CharField(_("name"), max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(_("description"), blank=True, null=True)
    delivery_time = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        CREATED = 'CREATED', _('Created')
        DELIVERED = 'DELIVERED', _('Delivered')
        CANCELLED = 'CANCELLED', _('Cancelled')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.CREATED)
    address = models.CharField(_('address'), max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    phone_number = models.CharField(max_length=20, validators=[phone_number_validator])
    total_price = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='orders/images/', blank=True, null=True, verbose_name=_('Order Image'))

    is_confirmed = models.BooleanField(default=False, verbose_name=_('Is Confirmed'))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order #{self.id} - {self.user.full_name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        total_price = sum(cart_item.amount for cart_item in self.cart_items.all())
        if self.total_price != total_price:
            self.total_price = total_price
            super().save(update_fields=['total_price'])


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='cart_items', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def calculate_amount(self):
        if self.product and self.quantity:
            self.amount = self.product.price * self.quantity
        else:
            self.amount = 0
        return self.amount

    def __str__(self):
        return f"{self.product.name} - {self.user.full_name}"

    def save(self, *args, **kwargs):
        self.calculate_amount()
        super().save(*args, **kwargs)

        if self.order:
            order = self.order
            order.total_price = sum(item.amount for item in order.cart_items.all())
            order.save(update_fields=['total_price'])
