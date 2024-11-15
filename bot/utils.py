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
        "successful_changed": "Muvaffaqiyatli o'zgartirildi",
        "select_language": "Til tanlang!",
        'categories': 'Kategoriyalar',
        "my_orders": "📦 Mening buyurtmalarim",
        "contact_us": "📲 Biz bilan bog‘lanish",
        "settings": "⚙️ Sozlamalar",
        "full_name": "Iltimos to'liq ismni kiriting",
        "contact": "Iltimos raqamiz kiriting Namuna: +998 93 068 29 11",
        "successful_registration": "Muvaffaqiyatli ro'yxatdan o'tdi",
        "sorry": "Kechirasiz, boshqa raqamni sinab ko'ring",

    },

    "ru": {
        "successful_changed": "Муваффақиятли ўзгартирилди",
        "select_language": "Тил танланг!",
        'categories': 'Категориялар',
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
    'uz':
        """
     💧 Chere Suv Kompaniyasi <a href="@pdf_2905_bot">Chere Water</a> ni taqdim etadi 💧
    
    Chere suvi bilan bog'liq barcha masalalaringizni hal qiling! 🚰
    
    Bot nimalarni qila oladi?
    - Suv buyurtma qilish
    - So'nggi suv tariflarini bilish
    - Hisob-kitoblarni tekshirish
    - Eksklyuziv chegirmalar va aksiyalar haqida xabardor bo'lish
    - Savollar va yordam
    🌐 ChereBot – oson va tezkor xizmat! 
    
    🏠 Uyda qolib unikal xizmatlardan foydalaning!
    
    🟢 Hoziroq qo'shiling: <a href="@pdf_2905_bot">Chere Water</a>
    ✉️ Telegram kanal: <a href="@pdf_2905_bot">Chere Water</a>
    
    Chere - Sof Suv, Sog‘lom Hayot!
    """,

    "ru":

        """
    👕💧 Чере Сув Компанияси href="@pdf_2905_bot">Чере Wатер ни тақдим этади 💧

    Чере суви билан боғлиқ барча масалаларингизни ҳал қилинг! 🚰
    
    Бот нималарни қила олади?
    - Сув буюртма қилиш
    - Сўнгги сув тарифларини билиш
    - Ҳисоб-китобларни текшириш
    - Эксклюзив чегирмалар ва акциялар ҳақида хабардор бўлиш
    - Саволлар ва ёрдам
    🌐 ЧереБот – осон ва тезкор хизмат!
    
    🏠 Уйда қолиб уникал хизматлардан фойдаланинг!
    
    🟢 Ҳозироқ қўшилинг: href="@pdf_2905_bot">Чере Wатер
    ✉️ Телеграм канал: href="@pdf_2905_bot">Чере Wатер
    
    Чере - Соф Сув, Соғлом Ҳаёт!

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
