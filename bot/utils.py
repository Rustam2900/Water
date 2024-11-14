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
        "full_name": "Iltimos to'liq ismni kiriting",
        "contact": "Iltimos raqamiz kiriting Namuna: +998 93 068 29 11",
        "successful_registration": "Muvaffaqiyatli ro'yxatdan o'tdi",
        "sorry": "Kechirasiz, boshqa raqamni sinab ko'ring",


    },

    "ru": {
        "full_name": "Илтимос тўлиқ исмни киритинг",
        "contact": "Илтимос рақамиз киритинг Намуна: +998 93 068 29 11",
        "successful_registration": "Муваффақиятли рўйхатдан ўтди",
        "sorry": "Кечирасиз, бошқа рақамни синаб кўринг",

    }
}

user_languages = {}
local_user = {}

introduction_template = {
    'ru':
        """
    👕 Магазин Sneaker World <a href="https://t.me/sneaker_world_bot">Sneaker World</a> представляет!

    Что может сделать бот?

    Заказ одежды
    Информация о последних модных трендах
    Проверка счетов
    Будьте в курсе эксклюзивных скидок и акций
    Вопросы и помощь
    🌐 SneakerBot - легкий и быстрый сервис!

    🏠 Оставайтесь дома и пользуйтесь уникальными услугами!

    🟢 Присоединяйтесь прямо сейчас: <a href="https://t.me/sneaker_world_bot">Sneaker World</a>
    ✉️ Телеграм канал: <a href="https://t.me/sneaker_world_bot">Sneaker World</a>

    Sneaker World - Ваш стиль!
    """,

    "en":

        """
    👕 Sneaker World shop <a href="https://t.me/sneaker_world_bot">Sneaker World</a> presents!

    What can the bot do?

    Place clothing orders
    Get information about the latest fashion trends
    Check accounts
    Stay informed about exclusive discounts and promotions
    Questions and assistance
    🌐 SneakerBot - an easy and quick service!

    🏠 Stay at home and enjoy unique services!

    🟢 Join now: <a href="https://t.me/sneaker_world_bot">Sneaker World</a>
    ✉️ Telegram channel: <a href="https://t.me/sneaker_world_bot">Sneaker World</a>

    Sneaker World - Your Style!

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
