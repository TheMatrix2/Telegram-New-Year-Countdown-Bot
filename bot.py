import random
from datetime import time
from telegram import Update
from telegram.ext import Application, CommandHandler

from utils.chats import load_chats, days_until_new_year
from utils.commands import start, stop, check_now, get_chat_id
from utils.messages import send_daily_message
from utils.setup import BOT_TOKEN, TIMEZONE_STR, USE_ENV, TIMEZONE


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