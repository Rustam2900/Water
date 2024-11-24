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
    state = models.ForeignKey("bot.State", on_delete=models.SET_NULL, null=True, blank=True)
    county = models.ForeignKey("bot.County", on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.full_name


class Product(models.Model):
    name = models.CharField(_("name"), max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_time = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items_user')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items_product')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='cart_items', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_amount(self):
        if self.product and self.quantity:
            self.amount = self.product.price * self.quantity
        else:
            self.amount = 0
        return self.amount

    def __str__(self):
        return f"{self.product.name} - {self.user.full_name}"


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        CREATED = 'YARATILGAN', _('YARATILGAN')
        PAYED = "TO'LLANGAN", _("TO'LLANGAN")
        DELIVERED = 'DELIVERED', _('Delivered')
        CANCELLED = 'CANCELLED', _('Cancelled')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.CREATED)
    address = models.CharField(_('address'), max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    phone_number = models.CharField(max_length=20, validators=[phone_number_validator], blank=True, null=True)
    total_price = models.DecimalField(decimal_places=2, max_digits=10, default=0.00, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False, verbose_name=_('Is Confirmed'))

    def __str__(self):
        return f"Order #{self.id} - {self.user.full_name}"


class OrderMinSum(models.Model):
    min_order_sum = models.CharField(_("order minimum sum"), max_length=255)

    class Meta:
        verbose_name = _("Order minimum sum")
        verbose_name_plural = _("Order minimum sum")


class State(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = _("State")
        verbose_name_plural = _("States")

    def __str__(self):
        return self.name


class County(models.Model):
    name = models.CharField(_("name"), blank=True, max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="counties")

    class Meta:
        verbose_name = _("County")
        verbose_name_plural = _("Counties")

    def __str__(self):
        return self.name


class BlockedUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    full_name = models.CharField(_("full name"), blank=True, max_length=255)
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    phone_number = models.CharField(blank=True, unique=True, validators=[phone_number_validator],
                                    max_length=20)
    blocked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
