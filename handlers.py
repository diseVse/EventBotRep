from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from keyboards import *
from states import UserState

router = Router()

selected_city = {}


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет 👋\nВыбери действие:",
        reply_markup=main_menu()
    )


# ГОРОД
@router.message(F.text == "🏙 Выбрать город")
async def choose_city(message: Message, state: FSMContext):
    await state.set_state(UserState.choosing_city)

    await message.answer(
        "Выберите город:",
        reply_markup=cities_keyboard()
    )


@router.message(UserState.choosing_city)
async def save_city(message: Message, state: FSMContext):
    selected_city[message.from_user.id] = message.text

    await message.answer(
        f"Город выбран: {message.text}",
        reply_markup=main_menu()
    )

    await state.clear()


# ПО ЖАНРУ
@router.message(F.text == "🎭 По жанру")
async def choose_genre(message: Message, state: FSMContext):
    await state.set_state(UserState.choosing_genre)

    await message.answer(
        "Выберите жанр:",
        reply_markup=genres_keyboard()
    )


@router.message(UserState.choosing_genre)
async def genre_events(message: Message, state: FSMContext):
    genre = message.text

    events = {
        "Концерты": [
            "Imagine Dragons — 20 мая",
            "Rammstein — 1 июня"
        ],
        "Театр": [
            "Гамлет — 15 мая"
        ],
        "Стендап": [
            "StandUp Show — 18 мая"
        ]
    }

    text = "\n".join(events.get(genre, ["Нет мероприятий"]))

    await message.answer(
        f"Ближайшие события:\n\n{text}",
        reply_markup=main_menu()
    )

    await state.clear()


# БЛИЖАЙШИЕ
@router.message(F.text == "🔥 Ближайшие мероприятия")
async def nearest_events(message: Message):
    await message.answer(
        "🔥 Ближайшие мероприятия:\n\n"
        "• Концерт — завтра\n"
        "• Театр — через 2 дня\n"
        "• Стендап — через 3 дня"
    )


# ПО ДАТЕ
@router.message(F.text == "📅 Мероприятия по дате")
async def by_date(message: Message):
    await message.answer(
        "Введите дату в формате ДД.ММ.ГГГГ\n\n"
        "Например: 15.05.2026"
    )


@router.message(F.text.regexp(r"\d{2}\.\d{2}\.\d{4}"))
async def date_events(message: Message):
    await message.answer(
        f"Мероприятия на {message.text}:\n\n"
        "• Концерт Imagine Dragons\n"
        "• StandUp вечер",
        reply_markup=reminder_keyboard()
    )


# НАПОМИНАНИЯ
@router.callback_query(F.data.startswith("remind"))
async def reminder(callback: CallbackQuery):
    if callback.data == "remind_1":
        text = "Напоминание придет за 1 час"
    else:
        text = "Напоминание придет за 1 день"

    await callback.message.answer(text)

    await callback.answer()


# ДОНАТЫ В STARS
@router.message(F.text == "⭐ Донат")
async def donate(message: Message):
    prices = [LabeledPrice(label="Поддержка проекта", amount=100)]

    await message.answer_invoice(
        title="Поддержать бота",
        description="Спасибо за поддержку ❤️",
        payload="donate_payload",
        provider_token="",
        currency="XTR",
        prices=prices
    )
