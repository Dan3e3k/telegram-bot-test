
from database import init_db, add_reminder, get_user_reminders

# Создаём таблицу, если её ещё нет
init_db()

# Добавляем тестовое напоминание
reminder_id = add_reminder(
    telegram_id=123456789,
    text="Тест подключения базы",
    remind_at="2099-01-01 12:00:00"
)

print("Создано напоминание с ID:", reminder_id)

# Получаем напоминания конкретного пользователя
reminders = get_user_reminders(123456789)

print("Напоминания пользователя:")

for reminder in reminders:
    print(reminder)
