import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from config import BOT_TOKEN
from database import init_db, save_user, get_user_city, add_reminder, get_pending_reminders, mark_reminder_sent
from events_data import (
    get_events_by_city, get_events_by_city_and_date, 
    get_upcoming_events_by_genre, get_all_genres, EVENTS
)
from keyboards import (
    main_menu_keyboard, cities_keyboard, genres_keyboard,
    events_list_keyboard, event_detail_keyboard, remind_times_keyboard
)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Временное хранилище выбранного города пользователя
user_temp_city = {}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Сохраняем пользователя (город пока не выбран)
    save_user(user_id, username, "не выбран")
    
    await message.answer(
        "🎉 Добро пожаловать в EventBot!\n\n"
        "Я помогу тебе найти интересные мероприятия в твоём городе.\n\n"
        "🔹 Ищи события по дате через календарь\n"
        "🔹 Смотри ближайшие события по жанрам\n"
        "🔹 Ставь напоминания, чтобы ничего не пропустить\n\n"
        "Для начала выбери город:",
        reply_markup=cities_keyboard()
    )

@dp.callback_query(lambda c: c.data.startswith("city_"))
async def process_city(callback: CallbackQuery):
    city = callback.data.split("_", 1)[1]
    user_id = callback.from_user.id
    
    save_user(user_id, callback.from_user.username, city)
    user_temp_city[user_id] = city
    
    await callback.message.edit_text(
        f"✅ Город **{city}** сохранён!\n\n"
        f"Теперь выбери, что хочешь сделать:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "change_city")
async def change_city(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери город:",
        reply_markup=cities_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    user_id = callback.from_user.id
    city = get_user_city(user_id) or "не выбран"
    
    await callback.message.edit_text(
        f"🏠 Главное меню\nгород: {city}",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "search_by_date")
async def search_by_date(callback: CallbackQuery):
    user_id = callback.from_user.id
    city = get_user_city(user_id)
    
    if not city or city == "не выбран":
        await callback.message.edit_text(
            "Сначала выбери город!",
            reply_markup=cities_keyboard()
        )
        await callback.answer()
        return
    
    # Показываем календарь
    await callback.message.edit_text(
        f"📅 Выбери дату для поиска в городе {city}:",
        reply_markup=await SimpleCalendar().start_calendar()
    )
    await callback.answer()

@dp.callback_query(SimpleCalendarCallback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback):
    user_id = callback.from_user.id
    city = get_user_city(user_id)
    
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)
    
    if selected:
        selected_date = date.strftime("%Y-%m-%d")
        events = get_events_by_city_and_date(city, selected_date)
        
        if events:
            await callback.message.edit_text(
                f"📅 Мероприятия на {selected_date} в {city}:",
                reply_markup=events_list_keyboard(events)
            )
        else:
            await callback.message.edit_text(
                f"😕 На {selected_date} в {city} нет мероприятий.\n\n"
                f"Попробуй другую дату или поищи по жанрам:",
                reply_markup=main_menu_keyboard()
            )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "search_by_genre")
async def search_by_genre(callback: CallbackQuery):
    user_id = callback.from_user.id
    city = get_user_city(user_id)
    
    if not city or city == "не выбран":
        await callback.message.edit_text(
            "Сначала выбери город!",
            reply_markup=cities_keyboard()
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        f"🎭 Выбери жанр (будут показаны ближайшие события в {city} на неделю):",
        reply_markup=genres_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("genre_"))
async def show_events_by_genre(callback: CallbackQuery):
    genre = callback.data.split("_")[1]
    user_id = callback.from_user.id
    city = get_user_city(user_id)
    genres_dict = get_all_genres()
    genre_name = genres_dict.get(genre, genre)
    
    events = get_upcoming_events_by_genre(city, genre, days_ahead=7)
    
    if events:
        await callback.message.edit_text(
            f"🎭 {genre_name} в {city} (ближайшая неделя):\n\n"
            f"Найдено {len(events)} событий",
            reply_markup=events_list_keyboard(events)
        )
    else:
        await callback.message.edit_text(
            f"😕 В ближайшую неделю в {city} нет мероприятий в жанре {genre_name}.\n\n"
            f"Попробуй другой жанр:",
            reply_markup=genres_keyboard()
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("event_"))
async def show_event_detail(callback: CallbackQuery):
    event_id = int(callback.data.split("_")[1])
    event = next((e for e in EVENTS if e["id"] == event_id), None)
    
    if event:
        text = (
            f"🎫 **{event['name']}**\n\n"
            f"📍 Город: {event['city']}\n"
            f"📅 Дата: {event['date']}\n"
            f"⏰ Время: {event['time']}\n"
            f"🏛 Место: {event['venue']}\n"
            f"💰 Цена: {event['price']}\n"
            f"🎭 Жанр: {event['genre_name']}\n\n"
            f"📝 {event['description']}"
        )
        await callback.message.edit_text(
            text,
            parse_mode="Markdown",
            reply_markup=event_detail_keyboard(event_id)
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("set_remind_"))
async def set_reminder(callback: CallbackQuery):
    event_id = int(callback.data.split("_")[2])
    event = next((e for e in EVENTS if e["id"] == event_id), None)
    
    if event:
        await callback.message.edit_text(
            f"⏰ Напомнить о событии **{event['name']}** {event['date']} в {event['time']}\n\n"
            f"Выбери, когда прислать напоминание:",
            parse_mode="Markdown",
            reply_markup=remind_times_keyboard(event['name'], event['date'])
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("remind_"))
async def process_remind_time(callback: CallbackQuery):
    parts = callback.data.split("_")
    if len(parts) >= 3:
        time_type = parts[1]  # 1h, 2h, 1d, 2d
        event_name = "_".join(parts[2:-1]) if len(parts) > 4 else parts[2]
        event_date = parts[-1]
        
        user_id = callback.from_user.id
        
        # Вычисляем время напоминания
        event_datetime = datetime.strptime(f"{event_date} 19:00", "%Y-%m-%d %H:%M")
        
        if time_type == "1h":
            remind_time = event_datetime - timedelta(hours=1)
        elif time_type == "2h":
            remind_time = event_datetime - timedelta(hours=2)
        elif time_type == "1d":
            remind_time = event_datetime - timedelta(days=1)
        elif time_type == "2d":
            remind_time = event_datetime - timedelta(days=2)
        else:
            remind_time = event_datetime - timedelta(hours=1)
        
        add_reminder(user_id, event_name, event_date, remind_time)
        
        await callback.message.edit_text(
            f"✅ Напоминание о **{event_name}** установлено на {remind_time.strftime('%d.%m.%Y %H:%M')}\n\n"
            f"Я пришлю уведомление вовремя!",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "no_remind")
async def no_remind(callback: CallbackQuery):
    await callback.message.edit_text(
        "❌ Напоминание не установлено. Вернуться в главное меню:",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "donate")
async def donate(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐ **Поддержать бота звёздами** ⭐\n\n"
        "Ты можешь отправить донат в Telegram Stars!\n\n"
        "⭐ 50 звёзд — спасибо за поддержку!\n"
        "⭐ 100 звёзд — ты супер!\n"
        "⭐ 250 звёзд — легенда!\n\n"
        "Нажми на кнопку ниже, чтобы отправить донат:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Отправить 50 звёзд", callback_data="donate_50")],
            [InlineKeyboardButton(text="⭐ Отправить 100 звёзд", callback_data="donate_100")],
            [InlineKeyboardButton(text="⭐ Отправить 250 звёзд", callback_data="donate_250")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
        ])
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("donate_"))
async def process_donate(callback: CallbackQuery):
    amount = int(callback.data.split("_")[1])
    
    # Создаём инвойс для Telegram Stars
    # Telegram Stars — это специальный тип валюты с кодом "XTR"
    prices = [LabeledPrice(label="Поддержка бота", amount=amount)]
    
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="⭐ Поддержка EventBot",
        description=f"Спасибо за поддержку! Ты отправляешь {amount} звёзд.",
        payload="donation",
        provider_token="",  # Для Stars можно оставить пустым
        currency="XTR",  # XTR = Telegram Stars
        prices=prices,
        need_name=False,
        need_phone_number=False,
        need_email=False
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@dp.message(lambda m: m.successful_payment)
async def successful_payment(message: Message):
    amount = message.successful_payment.total_amount
    await message.answer(
        f"🎉 Спасибо за поддержку!\n\n"
        f"Ты отправил {amount} звёзд ⭐\n"
        f"Это очень помогает развитию бота!",
        reply_markup=main_menu_keyboard()
    )

@dp.callback_query(lambda c: c.data == "my_reminders")
async def my_reminders(callback: CallbackQuery):
    # Простая заглушка для списка напоминаний
    await callback.message.edit_text(
        "⏰ Здесь будет список твоих активных напоминаний.\n\n"
        "(Функция в разработке)",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_events")
async def back_to_events(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери мероприятие:",
        reply_markup=events_list_keyboard(EVENTS[:3])
    )
    await callback.answer()

async def check_reminders():
    """Фоновая задача для проверки напоминаний"""
    while True:
        reminders = get_pending_reminders()
        for rem_id, user_id, event_name, event_date, remind_time in reminders:
            try:
                await bot.send_message(
                    user_id,
                    f"🔔 **Напоминание!**\n\n"
                    f"Событие: {event_name}\n"
                    f"Дата: {event_date}\n\n"
                    f"Не пропусти! 👀",
                    parse_mode="Markdown"
                )
                mark_reminder_sent(rem_id)
            except Exception as e:
                logging.error(f"Ошибка отправки напоминания: {e}")
        await asyncio.sleep(60)  # Проверяем каждую минуту

async def main():
    init_db()
    
    # Запускаем фоновую задачу для напоминаний
    asyncio.create_task(check_reminders())
    
    await dp.start_polling(bot)
    logging.info("Бот запущен!")

if __name__ == "__main__":
    asyncio.run(main())
