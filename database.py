import sqlite3
from datetime import datetime, timedelta
from config import BONUS_EXPIRE_DAYS

DB_NAME = "users.db"


def init_db():
    """Создаёт таблицы, если их нет"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            last_update TEXT,                -- дата обновления баланса
            expire_date TEXT,                -- дата сгорания
            city TEXT,
            store_address TEXT,
            notify_enabled INTEGER DEFAULT 1 -- 1 - включены напоминания
        )
    ''')

    # Таблица для истории товаров (опционально)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            store_city TEXT,
            updated_at TEXT
        )
    ''')

    conn.commit()
    conn.close()


def get_user(user_id):
    """Получить данные пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT balance, last_update, expire_date, city, store_address, notify_enabled FROM users WHERE user_id = ?',
        (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "balance": row[0],
            "last_update": row[1],
            "expire_date": row[2],
            "city": row[3],
            "store_address": row[4],
            "notify_enabled": bool(row[5])
        }
    return None


def set_balance(user_id, balance):
    """Сохранить баланс и рассчитать дату сгорания"""
    today = datetime.now().isoformat()
    expire = (datetime.now() + timedelta(days=BONUS_EXPIRE_DAYS)).isoformat()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, balance, last_update, expire_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, balance, today, expire))
    conn.commit()
    conn.close()


def set_city(user_id, city):
    """Сохранить город пользователя"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET city = ? WHERE user_id = ?', (city, user_id))
    conn.commit()
    conn.close()


def set_store_address(user_id, address):
    """Сохранить адрес магазина"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET store_address = ? WHERE user_id = ?', (address, user_id))
    conn.commit()
    conn.close()


def set_notify(user_id, enabled):
    """Включить/отключить уведомления"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET notify_enabled = ? WHERE user_id = ?', (1 if enabled else 0, user_id))
    conn.commit()
    conn.close()


def get_all_users():
    """Получить список всех user_id (для рассылки)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, balance, expire_date, notify_enabled FROM users')
    rows = cursor.fetchall()
    conn.close()
    return rows