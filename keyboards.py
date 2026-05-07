from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏙 Выбрать город")],
            [KeyboardButton(text="📅 Мероприятия по дате")],
            [KeyboardButton(text="🎭 По жанру")],
            [KeyboardButton(text="🔥 Ближайшие мероприятия")],
            [KeyboardButton(text="⭐ Донат")]
        ],
        resize_keyboard=True
    )


def cities_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Москва")],
            [KeyboardButton(text="Санкт-Петербург")],
            [KeyboardButton(text="Казань")]
        ],
        resize_keyboard=True
    )


def genres_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Концерты")],
            [KeyboardButton(text="Театр")],
            [KeyboardButton(text="Стендап")]
        ],
        resize_keyboard=True
    )


def reminder_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Напомнить за 1 час",
                    callback_data="remind_1"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Напомнить за 1 день",
                    callback_data="remind_24"
                )
            ]
        ]
    )
