
import sqlite3
from pathlib import Path


# Путь к базе данных рядом с этим файлом
DB_PATH = Path(__file__).resolve().parent / "bot.db"


def init_db():
    """Создаёт таблицу напоминаний, если её ещё нет."""
    connection = sqlite3.connect(DB_PATH)

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                is_sent INTEGER NOT NULL DEFAULT 0
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                username TEXT,
                name TEXT NOT NULL,
                contact TEXT NOT NULL,
                description TEXT NOT NULL,
                voice_file_id TEXT,
                created_at TEXT NOT NULL
            )
        """)

        connection.commit()
    finally:
        connection.close()


def add_reminder(telegram_id, text, remind_at):
    """Добавляет напоминание и возвращает его ID."""
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute("""
            INSERT INTO reminders (telegram_id, text, remind_at)
            VALUES (?, ?, ?)
        """, (telegram_id, text, remind_at))

        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def get_user_reminders(telegram_id):
    """Возвращает неотправленные напоминания пользователя."""
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute("""
            SELECT id, telegram_id, text, remind_at, is_sent
            FROM reminders
            WHERE telegram_id = ? AND is_sent = 0
            ORDER BY remind_at
        """, (telegram_id,))

        return cursor.fetchall()
    finally:
        connection.close()


def get_due_reminders(current_time):
    """Находит все напоминания, время которых наступило."""
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute("""
            SELECT id, telegram_id, text, remind_at, is_sent
            FROM reminders
            WHERE is_sent = 0 AND remind_at <= ?
            ORDER BY remind_at
        """, (current_time,))

        return cursor.fetchall()
    finally:
        connection.close()


def mark_reminder_sent(reminder_id):
    """Отмечает напоминание как отправленное."""
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute("""
            UPDATE reminders
            SET is_sent = 1
            WHERE id = ? AND is_sent = 0
        """, (reminder_id,))

        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()


def delete_reminder(reminder_id, telegram_id):
    """Удаляет напоминание только у его владельца."""
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute("""
            DELETE FROM reminders
            WHERE id = ? AND telegram_id = ?
        """, (reminder_id, telegram_id))

        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()

from datetime import datetime


def save_order(
    telegram_id,
    username,
    name,
    contact,
    description,
    voice_file_id=None,
):
    """Сохраняет заявку клиента в базу данных."""

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute("""
            INSERT INTO orders (
                telegram_id,
                username,
                name,
                contact,
                description,
                voice_file_id,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            telegram_id,
            username,
            name,
            contact,
            description,
            voice_file_id,
            datetime.now().isoformat(timespec="seconds"),
        ))

        connection.commit()
        return cursor.lastrowid

    finally:
        connection.close()
