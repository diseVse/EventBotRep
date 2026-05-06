from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

def main_menu_keyboard():
    kb = [
        [InlineKeyboardButton(text="🌆 Выбрать город", callback_data="change_city")],
        [InlineKeyboardButton(text="🗓 Искать по дате (календарь)", callback_data="search_by_date")],
        [InlineKeyboardButton(text="🎭 Искать ближайшие по жанру", callback_data="search_by_genre")],
        [InlineKeyboardButton(text="⏰ Мои напоминания", callback_data="my_reminders")],
        [InlineKeyboardButton(text="⭐ Поддержать донатом", callback_data="donate")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def genres_keyboard():
    from events_data import get_all_genres
    genres = get_all_genres()
    kb = []
    for key, name in genres.items():
        kb.append([InlineKeyboardButton(text=name, callback_data=f"genre_{key}")])
    kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def cities_keyboard():
    kb = [
        [InlineKeyboardButton(text="📍 Москва", callback_data="city_Москва")],
        [InlineKeyboardButton(text="📍 Санкт-Петербург", callback_data="city_Санкт-Петербург")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def remind_times_keyboard(event_name, event_date):
    """Клавиатура для выбора времени напоминания"""
    kb = [
        [InlineKeyboardButton(text="🔔 За 1 час", callback_data=f"remind_1h_{event_name}_{event_date}")],
        [InlineKeyboardButton(text="🔔 За 2 часа", callback_data=f"remind_2h_{event_name}_{event_date}")],
        [InlineKeyboardButton(text="🔔 За 1 день", callback_data=f"remind_1d_{event_name}_{event_date}")],
        [InlineKeyboardButton(text="🔔 За 2 дня", callback_data=f"remind_2d_{event_name}_{event_date}")],
        [InlineKeyboardButton(text="❌ Не напоминать", callback_data="no_remind")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def events_list_keyboard(events):
    """Клавиатура со списком мероприятий"""
    kb = []
    for event in events:
        kb.append([InlineKeyboardButton(
            text=f"{event['name']} - {event['date']} {event['time']}",
            callback_data=f"event_{event['id']}"
        )])
    kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def event_detail_keyboard(event_id):
    kb = [
        [InlineKeyboardButton(text="⏰ Напомнить", callback_data=f"set_remind_{event_id}")],
        [InlineKeyboardButton(text="🔙 Вернуться к списку", callback_data="back_to_events")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# Календарь будет создаваться через SimpleCalendar
