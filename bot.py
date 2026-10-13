
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


# =========================
# НАСТРОЙКИ
# =========================

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        f"Не найден BOT_TOKEN. Проверь файл: {env_path}"
    )

OWNER_ID = 729052410  # Твой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()


# =========================
# СОСТОЯНИЯ ЗАЯВКИ
# =========================

class OrderForm(StatesGroup):
    name = State()
    contact = State()
    description = State()


# =========================
# КЛАВИАТУРЫ
# =========================

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🤖 Создание бота")],
        [KeyboardButton(text="💰 Стоимость услуг")],
        [KeyboardButton(text="📝 Оставить заявку")],
    ],
    resize_keyboard=True,
)

confirm_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Всё верно",
                callback_data="confirm_order",
            ),
        ],
        [
            InlineKeyboardButton(
                text="✏️ Изменить заявку",
                callback_data="edit_order",
            ),
        ],
    ]
)

edit_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👤 Изменить имя",
                callback_data="edit_name",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📱 Изменить контакт",
                callback_data="edit_contact",
            ),
        ],
        [
            InlineKeyboardButton(
                text="📝 Изменить описание",
                callback_data="edit_description",
            ),
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Назад к заявке",
                callback_data="back_to_order",
            ),
        ],
    ]
)


# =========================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================

async def show_order(message: Message, state: FSMContext):
    """Показывает заполненную заявку для проверки."""

    data = await state.get_data()

    text = (
        "📋 Проверь свою заявку:\n\n"
        f"Имя: {data['name']}\n"
        f"Контакт: {data['contact']}\n"
        f"Описание: {data['description']}\n\n"
        "Всё правильно? Подтверди заявку "
        "или выбери редактирование."
    )

    await message.answer(
        text,
        reply_markup=confirm_keyboard,
    )


async def ask_for_name(message: Message, state: FSMContext):
    await state.set_state(OrderForm.name)
    await message.answer("Как тебя зовут? Напиши имя.")


async def ask_for_contact(message: Message, state: FSMContext):
    await state.set_state(OrderForm.contact)
    await message.answer(
        "Как с тобой связаться? Укажи Telegram или телефон."
    )


async def ask_for_description(message: Message, state: FSMContext):
    await state.set_state(OrderForm.description)
    await message.answer("Опиши, какой бот тебе нужен.")


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
    "Привет! 👋\n\n"
    "Я создаю Telegram-ботов, которые помогают бизнесу "
    "экономить время и упрощать работу с клиентами.\n\n"
    "Что можно автоматизировать:\n"
    "🤖 Приём и обработку заявок\n"
    "📅 Запись клиентов и бронирование\n"
    "💬 Ответы на частые вопросы\n"
    "⚙️ Другие процессы под задачи вашего бизнеса\n\n"
    "Посмотрите услуги или расскажите, какой бот нужен именно вам.\n"
    "Выберите действие в меню ниже 👇",
    reply_markup=menu
)


@dp.message(Command("cancel"))
async def cancel(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Заявка отменена.",
        reply_markup=menu,
    )


@dp.message(F.text == "🤖 Создание бота")
async def about_bot(message: Message):
    await message.answer(
        "🤖 Разработка Telegram-ботов для бизнеса\n\n"
        "Помогаю автоматизировать рутинные задачи и упростить "
        "взаимодействие с клиентами.\n\n"
        "Что могу реализовать:\n\n"
        "📩 Приём заявок и сбор контактов\n"
        "📅 Запись клиентов и бронирование\n"
        "💬 Меню с услугами, ценами и ответами на вопросы\n"
        "⚙️ Индивидуальные решения под задачи бизнеса\n\n"
        "Как проходит работа:\n"
        "1. Обсуждаем вашу задачу.\n"
        "2. Согласовываем функционал и стоимость.\n"
        "3. Я разрабатываю и настраиваю бота.\n\n"
        "Стоимость зависит от сложности проекта.\n"
        "Чтобы обсудить свою задачу, выберите "
        "«📝 Оставить заявку» в меню."
    )



@dp.message(F.text == "💰 Стоимость услуг")
async def prices(message: Message):
    text = (
        "<b>💰 Стоимость разработки Telegram-ботов</b>\n\n"

        "<b>1. Информационный бот</b>\n"
        "От 3 000 ₽\n"
        "• Меню с кнопками\n"
        "• Информация об услугах\n"
        "• Ответы на частые вопросы\n\n"

        "<b>2. Бот для приёма заявок</b>\n"
        "От 5 000 ₽\n"
        "• Форма сбора заявок\n"
        "• Получение заявок администратором\n"
        "• Уведомления о новых обращениях\n\n"

        "<b>3. Бот с расширенным функционалом</b>\n"
        "От 8 000 ₽\n"
        "• Индивидуальная логика работы\n"
        "• Интеграции и автоматизация\n"
        "• Дополнительные функции под задачи бизнеса\n\n"

        "<b>Дополнительные услуги</b>\n"
        "• Доработка существующего бота — от 1 000 ₽\n"
        "• Добавление новых функций — от 1 000 ₽\n"
        "• Подключение внешних сервисов — по договорённости\n\n"

        "<b>📌 Условия</b>\n"
        "• Итоговая стоимость зависит от сложности проекта\n"
        "• Перед началом согласовываем функционал и сроки\n"
        "• Хостинг оплачивается отдельно, если требуется\n\n"

        "Чтобы обсудить ваш проект, нажмите "
        "«Оставить заявку» 👇"
    )

    await message.answer(text, parse_mode="HTML")


# =========================
# НАЧАЛО ОФОРМЛЕНИЯ ЗАЯВКИ
# =========================

@dp.message(F.text == "📝 Оставить заявку")
async def order_start(message: Message, state: FSMContext):
    await state.clear()
    await ask_for_name(message, state)


# =========================
# ВВОД И РЕДАКТИРОВАНИЕ ПОЛЕЙ
# =========================

@dp.message(OrderForm.name, F.text)
async def order_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if not name:
        await message.answer("Имя не должно быть пустым. Попробуй ещё раз.")
        return

    await state.update_data(name=name)
    data = await state.get_data()

    # Если редактируем готовую заявку
    if data.get("contact") and data.get("description"):
        await state.set_state(None)
        await show_order(message, state)
        return

    await ask_for_contact(message, state)


@dp.message(OrderForm.contact, F.text)
async def order_contact(message: Message, state: FSMContext):
    contact = message.text.strip()

    if not contact:
        await message.answer(
            "Контакт не должен быть пустым. Попробуй ещё раз."
        )
        return

    await state.update_data(contact=contact)
    data = await state.get_data()

    # Если редактируем готовую заявку
    if data.get("name") and data.get("description"):
        await state.set_state(None)
        await show_order(message, state)
        return

    await ask_for_description(message, state)


@dp.message(OrderForm.description, F.text)
async def order_description(message: Message, state: FSMContext):
    description = message.text.strip()

    if not description:
        await message.answer(
            "Описание не должно быть пустым. Попробуй ещё раз."
        )
        return

    await state.update_data(description=description)
    await state.set_state(None)

    await show_order(message, state)


# =========================
# МЕНЮ РЕДАКТИРОВАНИЯ
# =========================

@dp.callback_query(F.data == "edit_order")
async def edit_order(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        "Что хочешь изменить?",
        reply_markup=edit_keyboard,
    )

    await callback.answer()


@dp.callback_query(F.data == "edit_name")
async def edit_name(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if not all(data.get(key) for key in ("name", "contact", "description")):
        await callback.answer(
            "Заявка не найдена. Начни заполнение заново.",
            show_alert=True,
        )
        await state.clear()
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await ask_for_name(callback.message, state)
    await callback.answer()


@dp.callback_query(F.data == "edit_contact")
async def edit_contact(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if not all(data.get(key) for key in ("name", "contact", "description")):
        await callback.answer(
            "Заявка не найдена. Начни заполнение заново.",
            show_alert=True,
        )
        await state.clear()
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await ask_for_contact(callback.message, state)
    await callback.answer()


@dp.callback_query(F.data == "edit_description")
async def edit_description(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if not all(data.get(key) for key in ("name", "contact", "description")):
        await callback.answer(
            "Заявка не найдена. Начни заполнение заново.",
            show_alert=True,
        )
        await state.clear()
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await ask_for_description(callback.message, state)
    await callback.answer()


@dp.callback_query(F.data == "back_to_order")
async def back_to_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if not all(data.get(key) for key in ("name", "contact", "description")):
        await callback.answer(
            "Заявка не найдена. Начни заполнение заново.",
            show_alert=True,
        )
        await state.clear()
        return

    await state.set_state(None)
    await callback.message.edit_reply_markup(reply_markup=None)
    await show_order(callback.message, state)
    await callback.answer()


# =========================
# ПОДТВЕРЖДЕНИЕ И ОТПРАВКА
# =========================

@dp.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if not all(data.get(key) for key in ("name", "contact", "description")):
        await callback.answer(
            "Данные заявки потеряны. Заполни её заново.",
            show_alert=True,
        )
        await state.clear()
        return

    username = callback.from_user.username
    username = f"@{username}" if username else "не указан"

    text = (
        "📩 Новая заявка!\n\n"
        f"Имя: {data['name']}\n"
        f"Контакт: {data['contact']}\n"
        f"Описание: {data['description']}\n"
        f"Telegram клиента: {username}"
    )

    try:
        await bot.send_message(OWNER_ID, text)

    except Exception as error:
        print(f"Ошибка отправки заявки: {error}")

        await callback.answer(
            "Не удалось отправить заявку. Попробуй ещё раз.",
            show_alert=True,
        )
        return

    await state.clear()

    await callback.message.edit_reply_markup(reply_markup=None)

    await callback.message.answer(
        "✅ Спасибо! Заявка отправлена. Скоро с тобой свяжутся.",
        reply_markup=menu,
    )

    await callback.answer("Заявка отправлена!")


# =========================
# ЗАПУСК
# =========================

async def main():
    print("Бот запущен!")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())