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

    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.CREATED)
    address = models.CharField(_('address'), max_length=255)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    phone_number = models.CharField(max_length=20)
    total_price = models.DecimalField(decimal_places=2, max_digits=10, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='orders/images/', blank=True, null=True, verbose_name=_('Order Image'))
    is_confirmed = models.BooleanField(default=False, verbose_name=_('Is Confirmed'))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return f"Order #{self.id} - {self.user.full_name}"

    def update_total_price(self):
        """Umumiy narxni hisoblash va yangilash."""
        total = self.cart_items.aggregate(total=Sum('amount'))['total'] or 0.00
        if self.total_price != total:
            self.total_price = total
            self.save(update_fields=['total_price'])


class CartItem(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='cart_items')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='cart_items', blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def calculate_amount(self):
        """Mahsulot narxini va miqdorini asosida `amount`ni hisoblash."""
        if self.product and self.quantity:
            self.amount = self.product.price * self.quantity
        else:
            self.amount = 0
        return self.amount

    def save(self, *args, **kwargs):
        self.calculate_amount()  # `amount`ni yangilash
        super().save(*args, **kwargs)

        if self.order:
            # Buyurtmaning umumiy narxini yangilash
            self.order.update_total_price()

    def __str__(self):
        return f"{self.product.name} - {self.user.full_name}"
