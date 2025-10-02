import os
import json
import random
from datetime import datetime, time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import pytz

# Попытка загрузить переменные из .env файла
try:
    from dotenv import load_dotenv

    load_dotenv()
    USE_ENV = True
except ImportError:
    USE_ENV = False

# Получаем конфигурацию из переменных окружения или используем значения по умолчанию
BOT_TOKEN = os.getenv("BOT_TOKEN", "BOT_TOKEN")
TIMEZONE_STR = os.getenv("TIMEZONE", "Europe/Moscow")

# Файл для хранения списка чатов
CHATS_FILE = "chats.json"

# Настройка часового пояса
try:
    TIMEZONE = pytz.timezone(TIMEZONE_STR)
except pytz.exceptions.UnknownTimeZoneError:
    print(f"Предупреждение: Неизвестный часовой пояс '{TIMEZONE_STR}', используется Europe/Moscow")
    TIMEZONE = pytz.timezone('Europe/Moscow')


def load_chats():
    """Загружает список чатов из файла"""
    try:
        with open(CHATS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_chats(chats):
    """Сохраняет список чатов в файл"""
    with open(CHATS_FILE, 'w') as f:
        json.dump(chats, f, indent=2)


def add_chat(chat_id, chat_type, chat_title):
    """Добавляет чат в список, если его там нет"""
    chats = load_chats()

    # Проверяем, есть ли уже этот чат
    for chat in chats:
        if chat['id'] == chat_id:
            return False

    # Добавляем новый чат
    chats.append({
        'id': chat_id,
        'type': chat_type,
        'title': chat_title,
        'added_at': datetime.now(TIMEZONE).isoformat()
    })
    save_chats(chats)
    return True


def remove_chat(chat_id):
    """Удаляет чат из списка"""
    chats = load_chats()
    chats = [chat for chat in chats if chat['id'] != chat_id]
    save_chats(chats)


def days_until_new_year():
    """Подсчитывает количество дней до Нового года"""
    now = datetime.now(TIMEZONE)
    current_year = now.year

    # Если сегодня 31 декабря, показываем 0 дней
    new_year = datetime(current_year + 1, 1, 1, tzinfo=TIMEZONE)

    days_left = (new_year.date() - now.date()).days
    return days_left


def word_after_number(days: int) -> str:
    """Формирует сообщение для отправки"""
    last_digit = days % 10
    last_two_digits = days % 100

    if last_digit == 1 and last_two_digits != 11:
        return 'день'
    elif last_digit in [2, 3, 4] and last_two_digits not in [12, 13, 14]:
        return 'дня'
    else:
        return 'дней'


def countdown_message():
    """Создает сообщение для отправки"""
    days = days_until_new_year()
    word = word_after_number(days)
    if days == 0:
        message = "🎉 С Новым Годом! 🎊"
    elif days == 1:
        message = f"🎄 Остался всего {days} {word} до Нового года! 🎅"
    elif days <= 4:
        message = f"🎄 Осталось {days} {word} до Нового года! 🎅"
    else:
        message = f"🎄 Осталось {days} {word} до Нового года! 🎅"
    return message


async def send_daily_message(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ежедневное сообщение с количеством дней до НГ во все чаты"""
    message = countdown_message()

    chats = load_chats()
    success_count = 0
    failed_chats = []

    for chat in chats:
        try:
            await context.bot.send_message(chat_id=chat['id'], text=message)
            success_count += 1
            print(f"[{datetime.now(TIMEZONE)}] Сообщение отправлено в {chat['title']} ({chat['id']})")
        except Exception as e:
            print(f"[{datetime.now(TIMEZONE)}] Ошибка отправки в {chat['title']} ({chat['id']}): {e}")
            failed_chats.append(chat['id'])

    # Удаляем чаты, куда не удалось отправить (возможно бот был удален)
    for chat_id in failed_chats:
        remove_chat(chat_id)

    print(f"[{datetime.now(TIMEZONE)}] Отправлено в {success_count}/{len(chats)} чатов")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start - подписывает чат на уведомления"""
    days = days_until_new_year()
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title if hasattr(update.effective_chat,
                                                        'title') else f"Личный чат ({update.effective_user.first_name})"

    # Добавляем чат в список
    is_new = add_chat(chat_id, chat_type, chat_title)

    # Логируем
    print(
        f"[{datetime.now(TIMEZONE)}] /start от {chat_title} ({chat_id}, {chat_type}) - {'новый чат' if is_new else 'уже подписан'}")

    if is_new:
        message = (
            f"✅ Отлично! Теперь я буду отправлять сюда каждый день количество дней до Нового года.\n\n"
            f"Сейчас до Нового года осталось: {days} {word_after_number(days)} 🎄\n\n"
            f"Команды:\n"
            f"/check - узнать количество дней прямо сейчас\n"
            f"/stop - отписаться от уведомлений\n"
            f"/chatid - узнать ID этого чата"
        )
    else:
        message = (
            f"Вы уже подписаны на уведомления! ✅\n\n"
            f"До Нового года осталось: {days} {word_after_number(days)} 🎄\n\n"
            f"Команды:\n"
            f"/check - узнать количество дней прямо сейчас\n"
            f"/stop - отписаться от уведомлений"
        )

    if chat_type in ['group', 'supergroup']:
        message += "\n\n📌 Это групповой чат. Убедитесь, что бот является администратором для отправки сообщений."

    await update.message.reply_text(message)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /stop - отписывает чат от уведомлений"""
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title if hasattr(update.effective_chat,
                                                        'title') else f"Личный чат ({update.effective_user.first_name})"

    remove_chat(chat_id)

    print(f"[{datetime.now(TIMEZONE)}] /stop от {chat_title} ({chat_id})")

    await update.message.reply_text(
        "😢 Вы отписались от уведомлений.\n\n"
        "Чтобы снова подписаться, отправьте /start"
    )


async def check_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /check - показывает актуальное количество дней"""
    message = countdown_message()

    await update.message.reply_text(message)


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /chatid - показывает ID чата"""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title if hasattr(update.effective_chat, 'title') else "Личный чат"

    message = (
        f"📋 Информация о чате:\n\n"
        f"Chat ID: `{chat_id}`\n"
        f"Тип: {chat_type}\n"
        f"Название: {chat_title}"
    )

    await update.message.reply_text(message, parse_mode='Markdown')


def main():
    """Основная функция запуска бота"""
    # Проверка конфигурации
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("ОШИБКА: Необходимо настроить BOT_TOKEN!")
        print("Отредактируйте bot.py или создайте файл .env")
        exit(1)

    chats = load_chats()

    print("=" * 50)
    print("🎄 Telegram New Year Countdown Bot")
    print("=" * 50)
    print(f"Часовой пояс: {TIMEZONE_STR}")
    print(f"Осталось дней до Нового года: {days_until_new_year()}")
    print(f"Конфигурация: {'из .env файла' if USE_ENV else 'из bot.py'}")
    print(f"Подписанных чатов: {len(chats)}")
    print("=" * 50)

    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("check", check_now))
    application.add_handler(CommandHandler("chatid", get_chat_id))

    # Получаем job_queue для планирования задач
    job_queue = application.job_queue

    # Планируем ежедневную отправку в 9:00 по указанному часовому поясу
    job_queue.run_daily(
        send_daily_message,
        time=time(hour=12, minute=random.randint(0, 59), tzinfo=TIMEZONE),
        name="daily_countdown"
    )

    print("✓ Бот запущен!")
    # print("✓ Ежедневные сообщения будут отправляться в 9:00")
    print("✓ Чтобы получать уведомления, отправьте боту /start")
    print("")

    # Запускаем бота
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\n\nБот остановлен пользователем")
    except Exception as e:
        print(f"\n\nОшибка: {e}")


if __name__ == "__main__":
    main()