from django.contrib import admin
from modeltranslation.admin import TranslationAdmin

from bot.models import CustomUser, Order


@admin.register(CustomUser)
class CustomUserAdmin(TranslationAdmin):
    list_display = ('id', 'username', 'phone_number')
    list_display_links = ('id', 'username', 'phone_number')
    search_fields = ('username', 'phone_number')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'total_price', 'created_at', 'phone_number', 'display_items')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'address', 'phone_number')
    readonly_fields = ('total_price', 'display_items')

    def display_items(self, obj):
        return "\n".join(
            [f"{item['name']} - {item['quantity']}x ({item['size']}, {item['color']})" for item in obj.items]
        )

    display_items.short_description = "Buyurtma mahsulotlari"
