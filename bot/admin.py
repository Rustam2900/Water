from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from bot.models import CustomUser, Order, Product, CartItem, OrderMinSum


@admin.register(CustomUser)
class CustomUserAdmin(TranslationAdmin):
    list_display = ('id', 'username', 'phone_number')
    list_display_links = ('id', 'username', 'phone_number')
    search_fields = ('username', 'phone_number')


@admin.register(Order)
class OrderAdmin(TranslationAdmin):
    list_display = ('user', 'status', 'total_price', 'created_at', 'phone_number', 'is_confirmed')

    list_filter = ('status', 'created_at', 'is_confirmed')

    search_fields = ('user__username', 'address', 'phone_number')

    actions = ['mark_as_confirmed']

    def mark_as_confirmed(self, request, queryset):
        updated_count = queryset.update(is_confirmed=True)
        self.message_user(request, f"{updated_count} buyurtmalar tasdiqlandi.")

    mark_as_confirmed.short_description = ("Tanlangan buyurtmalarni tasdiqlangan deb belgilang")


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ('name', 'price', 'delivery_time')
    search_fields = ('id', 'name')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'is_visible', 'created_at')
    list_filter = ('user', 'product', 'is_visible')
    search_fields = ('user__username', 'product__name')


admin.site.register(OrderMinSum)
