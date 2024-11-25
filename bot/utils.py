all_languages = ['uz', 'ru']

message_history = {}

default_languages = {
    "language_not_found": "Siz to'g'ri tilni tanlamadingiz!\n"
                          "Сиз тўғри тилни танламадингиз!",
    "welcome_message": "Assalomu alaykum, xush kelibsiz!\n"
                       "Quyidagi tillardan birini tanlang!\n\n"
                       "Ассалому алайкум, хуш келибсиз!\n"
                       "Қуйидаги тиллардан бирини танланг!",

    "uz": {
        "name_update": "To'liq ismni o'zgartirish",
        "phone_update": "Telefon raqamini o'zgartirish",
        "lang_update": "Tilni o'zgartirish",
        "full_name_update": "Sizning to'liq ismingiz muvaffaqiyatli yangilandi:",
        "admin_not": "👮🏻‍♂️ Uzur siz Admin emassiz",
        "admin": "️Admin",
        "admin_welcome": "👮🏻‍♂️Admin Xushkelibsiz",
        "back": "Orqaga",
        "country": "Tuman tanlang:",
        "state_": "Viloyat tanlang:",
        "order__": "To'lov amalga oshirildi va buyurtmangiz qabul qilindi! 😊",
        "min_order_required": "minimal buyurtma talab qilinadi",
        "min_order_error": "minimal buyurtma yetmadi",
        "send_receipt": "chek yuboring",
        "order": "Mening buyurtmalarim",
        "order_save": "Sizning buyurtmangiz qabul qilindi va saqlandi.",
        "send_location_order": "Buyurtmangizni tasdiqlash uchun manzilingizni yuboring.",
        "product_add_cart": "Mahsulot savatga qo'shildi!",
        "products_quantity_enter": "Mahsulot miqdorini kiriting:",
        "send_location": "Joylashuvni yuborish",
        "product_shopping_cart": "Sizning savatchangiz:",
        "product_not_cart": "Savatingiz boʻsh.",
        "cart": "🛒Savatcha",
        "place_order": "Buyurtma berish",
        "delivery_time": "Yetkazib berish ",
        "products_price": "Narxi",
        "products_description": "tavsifi",
        "products": "Mahsulotlar",
        "category_select": "mahsulotlar  tanlang",
        "order_not_found": "Buyurtma topilmadi!",
        "successful_changed": "Muvaffaqiyatli o'zgartirildi",
        "select_language": "Til tanlang!",
        'categories': 'Buyurtma berish',
        "my_orders": "📦 Mening buyurtmalarim",
        "contact_us": "📲 Biz bilan bog‘lanish",
        "settings": "⚙️ Sozlamalar",
        "full_name": "Iltimos to'liq ismni kiriting",
        "contact": "Iltimos raqamiz kiriting Namuna: +998 93 068 29 11",
        "contact_update": "Sizning telefon raqamingiz muvaffaqiyatli yangilandi:",
        "successful_registration": "Muvaffaqiyatli ro'yxatdan o'tdi",
        "sorry": "Kechirasiz, boshqa raqamni sinab ko'ring",

    },

    "ru": {
        "name_update": "Тўлиқ исмни ўзгартириш",
        "phone_update": "Телефон рақамини ўзгартириш",
        "lang_update": "Тилни ўзгартириш",
        "contact_update": "Сизнинг телефон рақамингиз муваффақиятли янгиланди:",
        "full_name_update": "Сизнинг тўлиқ исмингиз муваффақиятли янгиланди:",
        "admin_welcome": "👮🏻‍♂️️Админ Хушкелибсиз",
        "admin_not": "👮🏻‍♂️ Узур сиз Админ эмассиз",
        "admin": "Админ",
        "back": "Орқага",
        "country": "Туман танланг:",
        "state_": "Вилоят танланг:",
        "order__": "Тўлов амалга оширилди ва буюртмангиз қабул қилинди! 😊",
        "min_order_required": "минимал буюртма талаб қилинади",
        "min_order_error": "минимал буюртма етмади",
        "send_receipt": "чек юборинг",
        "order": "Менинг буюртмаларим",
        "order_save": "Сизнинг буюртмангиз қабул қилинди ва сақланди.",
        "send_location_order": "Буюртмангизни тасдиқлаш учун манзилингизни юборанг.",
        "product_add_cart": "Маҳсулот саватга қўшилди!",
        "products_quantity_enter": "Маҳсулот миқдорини киритинг:",
        "send_location": "Жойлашувни юбориш",
        "product_shopping_cart": "Сизнинг саватингиз:",
        "product_not_cart": "Саватингиз бўш.",
        "cart": "🛒Cаватча",
        "place_order": "Буюртма бериш",
        "delivery_time": "Етказиб бериш ",
        "products_price": "Hархи",
        "products_description": "тавсифи",
        "products": "Маҳсулотлар",
        "category_select": "маҳсулотлар танланг",
        "order_not_found": "Буюртма топилмади!",
        "successful_changed": "Муваффақиятли ўзгартирилди",
        "select_language": "Тил танланг!",
        'categories': 'Буюртма бериш',
        "my_orders": "📦 Менинг буюртмаларим",
        "contact_us": "📲 Биз билан боғланиш",
        "settings": "⚙️ Созламалар",
        "full_name": "Илтимос тўлиқ исмни киритинг",
        "contact": "Илтимос рақамиз киритинг Намуна: +998 93 068 29 11",
        "successful_registration": "Муваффақиятли рўйхатдан ўтди",
        "sorry": "Кечирасиз, бошқа рақамни синаб кўринг",

    }
}

user_languages = {}
local_user = {}

introduction_template = {
    'uz': """
<b>💧 Ruqiya Shifo</b>
Tanangiz va ruhingiz salomatligi uchun dam solingan tabiiy toza ichimlik suvi.

<b>🚛 Yetkazib berish bepul</b>
""",
    'ru': """
<b>💧 Руқия Шифо</b>
Танангиз ва руҳингиз саломатлиги учун дам солинган табиий тоза ичимлик суви.

<b>🚛 Етказиб бериш бепул</b>
"""
}

order_text = {
    "en": "Order number {} \n order status {}",
    "ru": "Номер заказа {} \n Статус заказа {}"
}


def fix_phone(phone):
    if "+" not in phone:
        return f"+{phone}"
    return phone
