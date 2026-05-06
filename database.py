import sqlite3
from datetime import datetime

DB_NAME = "events_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            city TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица напоминаний
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_name TEXT,
            event_date TEXT,
            remind_time TIMESTAMP,
            is_sent BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def save_user(user_id, username, city):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, city, created_at)
        VALUES (?, ?, ?, COALESCE((SELECT created_at FROM users WHERE user_id = ?), CURRENT_TIMESTAMP))
    ''', (user_id, username, city, user_id))
    conn.commit()
    conn.close()

def get_user_city(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT city FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def add_reminder(user_id, event_name, event_date, remind_time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reminders (user_id, event_name, event_date, remind_time)
        VALUES (?, ?, ?, ?)
    ''', (user_id, event_name, event_date, remind_time))
    conn.commit()
    conn.close()

def get_pending_reminders():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, user_id, event_name, event_date, remind_time 
        FROM reminders 
        WHERE is_sent = 0 AND remind_time <= datetime('now')
    ''')
    results = cursor.fetchall()
    conn.close()
    return results

def mark_reminder_sent(reminder_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE reminders SET is_sent = 1 WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()
