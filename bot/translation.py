from modeltranslation.translator import TranslationOptions, register
from bot import models


@register(models.CustomUser)
class CustomUserTranslation(TranslationOptions):
    fields = ('full_name', 'username')


@register(models.Order)
class ProductTranslation(TranslationOptions):
    fields = ('address',)


@register(models.Product)
class ProductTranslation(TranslationOptions):
    fields = ('name', 'description')
