import random
from datetime import time
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from utils.chats import load_chats
from utils.commands import start, stop, check_now, get_chat_id, set_time_custom, time_button_callback, set_time_start
from utils.messages import send_daily_message, days_until_new_year
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
    application.add_handler(CommandHandler("settime", set_time_start))
    application.add_handler(CallbackQueryHandler(time_button_callback))

    # Получаем job_queue для планирования задач
    job_queue = application.job_queue

    # Запускаем проверку каждую минуту вместо ежедневно
    job_queue.run_repeating(
        send_daily_message,
        interval=60,  # каждую минуту
        first=10,  # первый запуск через 10 секунд
        name="countdown_checker"
    )

    print("✓ Бот запущен!")
    print("✓ Сообщения будут отправляться в настроенное время")
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