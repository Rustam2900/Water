from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from bot.utils import default_languages


def get_languages(flag="lang"):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="O‘zbek 🇺🇿", callback_data=f"{flag}_uz"),
         InlineKeyboardButton(text="Кирилл  🇷🇺", callback_data=f"{flag}_ru")],
    ])
    return keyboard


def get_main_menu(language):
    main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text=default_languages[language]['categories'], ),
            KeyboardButton(text=default_languages[language]['contact_us'])
        ],
        [
            KeyboardButton(text=default_languages[language]['my_orders']),
            KeyboardButton(text=default_languages[language]['settings'])
        ],
        [
            KeyboardButton(text=default_languages[language]['cart'])
        ]

    ], resize_keyboard=True)
    return main_menu_keyboard
