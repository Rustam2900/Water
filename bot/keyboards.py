from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from bot.utils import default_languages


def get_languages(flag="lang"):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="O‘zbek 🇺🇿", callback_data=f"{flag}_uz"),
         InlineKeyboardButton(text="Кирилл  🇷🇺", callback_data=f"{flag}_ru")],
    ])
    return keyboard


def get_main_menu(user_lang):
    main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
        [
            KeyboardButton(text=default_languages[user_lang]['categories']),
            KeyboardButton(text=default_languages[user_lang]['contact_us'])
        ],
        [
            KeyboardButton(text=default_languages[user_lang]['my_orders']),
            KeyboardButton(text=default_languages[user_lang]['settings'])
        ],
        [
            KeyboardButton(text=default_languages[user_lang]['cart'])
        ]

    ], resize_keyboard=True)
    return main_menu_keyboard
