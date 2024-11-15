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
    total_price = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)

    items = models.JSONField(default=list, blank=True, help_text=_("Order items in JSON format"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def calculate_total_price(self):
        total = 0
        for item in self.items:
            product_price = item.get("price", 0)
            quantity = item.get("quantity", 1)
            total += product_price * quantity
        self.total_price = total
        return self.total_price

    def __str__(self):
        return f"Order #{self.id} - {self.user.full_name}"


class Product(models.Model):
    name = models.CharField(_("name"), max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(_("description"), blank=True, null=True)
    delivery_time = models.CharField(max_length=100)

    def __str__(self):
        return self.name
