
import os
import sqlite3
from pathlib import Path
from html import escape

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

router = Router()

DB_PATH = Path(__file__).resolve().parent / "bot.db"
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

STATUSES = {
    "new": "🆕 Новая",
    "work": "🛠 В работе",
    "done": "✅ Завершена",
    "cancelled": "❌ Отменена",
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def prepare_db():
    """Добавляет поле статуса в существующую таблицу, если его нет."""
    with get_db() as conn:
        exists = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='orders'"
        ).fetchone()

        if not exists:
            raise RuntimeError("В базе данных нет таблицы orders")

        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(orders)").fetchall()
        }

        if "status" not in columns:
            conn.execute(
                "ALTER TABLE orders "
                "ADD COLUMN status TEXT NOT NULL DEFAULT 'new'"
            )


def is_admin(user_id: int) -> bool:
    admin_id = int(os.getenv("ADMIN_ID", "0"))
    return admin_id != 0 and user_id == admin_id


def admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🆕 Новые заявки",
                callback_data="adm:list:new:0"
            ),
            InlineKeyboardButton(
                text="🛠 В работе",
                callback_data="adm:list:work:0"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📋 Все заявки",
                callback_data="adm:list:all:0"
            ),
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="adm:stats"
            ),
        ],
    ])


def list_keyboard(orders, status, page):
    buttons = []

    for order in orders:
        name = order["name"] or order["username"] or "Без имени"
        buttons.append([
            InlineKeyboardButton(
                text=f"#{order['id']} · {str(name)[:30]}",
                callback_data=f"adm:order:{order['id']}"
            )
        ])

    navigation = []
    if page > 0:
        navigation.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"adm:list:{status}:{page - 1}"
            )
        )

    if len(orders) == 10:
        navigation.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"adm:list:{status}:{page + 1}"
            )
        )

    if navigation:
        buttons.append(navigation)

    buttons.append([
        InlineKeyboardButton(
            text="🏠 В меню",
            callback_data="adm:home"
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.message(Command("admin"))
async def open_admin(message: Message):
    if not message.from_user or not is_admin(message.from_user.id):
        await message.answer("⛔ Доступ запрещён.")
        return

    try:
        prepare_db()
    except (sqlite3.Error, RuntimeError) as error:
        await message.answer(f"Ошибка базы данных: {error}")
        return

    await message.answer(
        "🔐 <b>Панель администратора</b>\n\nВыбери раздел:",
        reply_markup=admin_menu(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("adm:"))
async def admin_actions(callback: CallbackQuery):
    if not callback.from_user or not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return

    await callback.answer()

    try:
        prepare_db()
        data = callback.data.split(":")
        action = data[1]

        if action == "home":
            await callback.message.edit_text(
                "🔐 <b>Панель администратора</b>\n\nВыбери раздел:",
                reply_markup=admin_menu(),
                parse_mode="HTML",
            )
            return

        if action == "list":
            status = data[2]
            page = max(0, int(data[3]))
            offset = page * 10

            with get_db() as conn:
                if status == "all":
                    orders = conn.execute(
                        "SELECT * FROM orders ORDER BY id DESC "
                        "LIMIT 10 OFFSET ?",
                        (offset,),
                    ).fetchall()
                    total = conn.execute(
                        "SELECT COUNT(*) FROM orders"
                    ).fetchone()[0]
                else:
                    orders = conn.execute(
                        "SELECT * FROM orders WHERE status=? "
                        "ORDER BY id DESC LIMIT 10 OFFSET ?",
                        (status, offset),
                    ).fetchall()
                    total = conn.execute(
                        "SELECT COUNT(*) FROM orders WHERE status=?",
                        (status,),
                    ).fetchone()[0]

            title = (
                "Все заявки"
                if status == "all"
                else STATUSES.get(status, status)
            )

            if not orders:
                text = f"📋 <b>{title}</b>\n\nЗаявок пока нет."
            else:
                text = (
                    f"📋 <b>{title}</b>\n"
                    f"Всего: {total} · Страница: {page + 1}\n\n"
                    "Выбери заявку:"
                )

            await callback.message.edit_text(
                text,
                reply_markup=list_keyboard(orders, status, page),
                parse_mode="HTML",
            )
            return

        if action == "order":
            order_id = int(data[2])

            with get_db() as conn:
                order = conn.execute(
                    "SELECT * FROM orders WHERE id=?",
                    (order_id,),
                ).fetchone()

            if not order:
                await callback.message.edit_text(
                    "Заявка не найдена.",
                    reply_markup=admin_menu(),
                )
                return

            fields = set(order.keys())

            def value(field):
                return escape(str(order[field] or "—")) if field in fields else "—"

            status = order["status"] if "status" in fields else "new"
            text = (
                f"📝 <b>Заявка #{order['id']}</b>\n\n"
                f"Статус: {escape(STATUSES.get(status, status))}\n"
                f"Имя: {value('name')}\n"
                f"Username: {value('username')}\n"
                f"Telegram ID: {value('telegram_id')}\n"
                f"Контакт: {value('contact')}\n"
                f"Описание: {value('description')}\n"
                f"Дата: {value('created_at')}\n"
                f"Голосовое сообщение: {value('voice_file_id')}"
            )

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🛠 В работу",
                        callback_data=f"adm:set:{order_id}:work"
                    ),
                    InlineKeyboardButton(
                        text="✅ Завершить",
                        callback_data=f"adm:set:{order_id}:done"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="🆕 Вернуть в новые",
                        callback_data=f"adm:set:{order_id}:new"
                    ),
                    InlineKeyboardButton(
                        text="❌ Отменить",
                        callback_data=f"adm:set:{order_id}:cancelled"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="⬅️ К заявкам",
                        callback_data="adm:list:all:0"
                    ),
                    InlineKeyboardButton(
                        text="🏠 В меню",
                        callback_data="adm:home"
                    ),
                ],
            ])

            await callback.message.edit_text(
                text, reply_markup=keyboard, parse_mode="HTML"
            )
            return

        if action == "set":
            order_id = int(data[2])
            status = data[3]

            if status not in STATUSES:
                await callback.answer("Неизвестный статус", show_alert=True)
                return

            with get_db() as conn:
                cursor = conn.execute(
                    "UPDATE orders SET status=? WHERE id=?",
                    (status, order_id),
                )

            if cursor.rowcount == 0:
                await callback.message.edit_text(
                    "Заявка не найдена.",
                    reply_markup=admin_menu(),
                )
            else:
                await callback.message.edit_text(
                    f"✅ Статус заявки #{order_id}: "
                    f"{STATUSES[status]}",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📄 Открыть заявку",
                                callback_data=f"adm:order:{order_id}"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                text="🏠 В меню",
                                callback_data="adm:home"
                            )
                        ],
                    ]),
                )
            return

        if action == "stats":
            with get_db() as conn:
                total = conn.execute(
                    "SELECT COUNT(*) FROM orders"
                ).fetchone()[0]

                rows = conn.execute(
                    "SELECT status, COUNT(*) AS count "
                    "FROM orders GROUP BY status"
                ).fetchall()

            counts = {row["status"]: row["count"] for row in rows}
            text = f"📊 <b>Статистика заявок</b>\n\nВсего: {total}\n"

            for key, label in STATUSES.items():
                text += f"{escape(label)}: {counts.get(key, 0)}\n"

            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🏠 В меню",
                            callback_data="adm:home"
                        )
                    ]
                ]),
                parse_mode="HTML",
            )

    except (sqlite3.Error, ValueError, IndexError) as error:
        await callback.message.answer(
            f"Не удалось выполнить действие: {error}"
        )
