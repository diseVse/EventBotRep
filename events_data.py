from datetime import datetime, timedelta

# Демо-база мероприятий
EVENTS = [
    {
        "id": 1,
        "name": "Рок-концерт: Ночные Снайперы",
        "city": "Москва",
        "date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "time": "19:00",
        "genre": "rock",
        "genre_name": "Рок",
        "venue": "Клуб 16 Тонн",
        "price": "1500 руб.",
        "description": "Легендарный рок-концерт с лучшими хитами."
    },
    {
        "id": 2,
        "name": "Джазовый вечер",
        "city": "Москва",
        "date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "time": "20:00",
        "genre": "jazz",
        "genre_name": "Джаз",
        "venue": "Джаз-клуб Эссе",
        "price": "2000 руб.",
        "description": "Известные джазовые стандарты в живом исполнении."
    },
    {
        "id": 3,
        "name": "Стендап-вечер",
        "city": "Санкт-Петербург",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "time": "20:00",
        "genre": "standup",
        "genre_name": "Стендап",
        "venue": "Comedy Club",
        "price": "1200 руб.",
        "description": "Лучшие комики города. Будет смешно!"
    },
    {
        "id": 4,
        "name": "Выставка импрессионистов",
        "city": "Москва",
        "date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
        "time": "11:00",
        "genre": "art",
        "genre_name": "Выставка",
        "venue": "Музей изобразительных искусств",
        "price": "800 руб.",
        "description": "Работы Моне, Ренуара и Дега."
    },
    {
        "id": 5,
        "name": "Электронная вечеринка",
        "city": "Санкт-Петербург",
        "date": (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"),
        "time": "23:00",
        "genre": "electronic",
        "genre_name": "Электроника",
        "venue": "Клуб А2",
        "price": "1000 руб.",
        "description": "Дип-хаус и техно до утра."
    },
    {
        "id": 6,
        "name": "Классический концерт: Бетховен",
        "city": "Москва",
        "date": (datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d"),
        "time": "19:30",
        "genre": "classical",
        "genre_name": "Классика",
        "venue": "Консерватория",
        "price": "2500 руб.",
        "description": "Симфония №5. Исполняет оркестр Мариинского театра."
    }
]

def get_events_by_city(city):
    return [e for e in EVENTS if e["city"].lower() == city.lower()]

def get_events_by_city_and_date(city, date):
    return [e for e in EVENTS if e["city"].lower() == city.lower() and e["date"] == date]

def get_events_by_city_and_genre(city, genre):
    return [e for e in EVENTS if e["city"].lower() == city.lower() and e["genre"] == genre]

def get_upcoming_events_by_genre(city, genre, days_ahead=7):
    """Ближайшие события по жанру (сейчас + N дней)"""
    today = datetime.now().strftime("%Y-%m-%d")
    future_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
    return [
        e for e in EVENTS 
        if e["city"].lower() == city.lower() 
        and e["genre"] == genre 
        and e["date"] >= today 
        and e["date"] <= future_date
    ]

def get_all_genres():
    return {
        "rock": "🎸 Рок",
        "jazz": "🎷 Джаз",
        "standup": "🎙 Стендап",
        "art": "🖼 Выставка",
        "electronic": "🪩 Электроника",
        "classical": "🎻 Классика"
    }
