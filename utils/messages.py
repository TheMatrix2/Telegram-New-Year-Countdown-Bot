from datetime import datetime, time
from telegram.ext import ContextTypes

from utils.chats import load_chats, remove_chat
from utils.setup import TIMEZONE


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
    last_digit = days % 10
    last_two_digits = days % 100
    if days == 0:
        message = "🎉 С Новым Годом! 🎊"
    elif last_digit == 1 and last_two_digits != 11:
        message = f"🎄 Остался всего {days} {word} до Нового года! 🎅"
    elif last_digit in [2, 3, 4] and last_two_digits not in [12, 13, 14]:
        message = f"🎄 Осталось {days} {word} до Нового года! 🎅"
    else:
        message = f"🎄 Осталось {days} {word} до Нового года! 🎅"
    return message


async def send_daily_message(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ежедневное сообщение с количеством дней до НГ во все чаты"""
    message = countdown_message()

    chats = load_chats()
    current_time = datetime.now(TIMEZONE).time()
    success_count = 0
    failed_chats = []

    for chat in chats:
        # Проверяем, нужно ли отправлять сообщение в этот чат сейчас
        time_start = chat.get('time_start', '09:00')
        time_end = chat.get('time_end', '09:00')

        # Парсим время
        start_hour, start_min = map(int, time_start.split(':'))
        end_hour, end_min = map(int, time_end.split(':'))

        start_time = time(hour=start_hour, minute=start_min)
        end_time = time(hour=end_hour, minute=end_min)

        # Проверяем, попадает ли текущее время в диапазон
        should_send = False
        if start_time == end_time:
            # Точное время (с допуском 1 минута)
            if abs((current_time.hour * 60 + current_time.minute) - (start_hour * 60 + start_min)) <= 1:
                should_send = True
        else:
            # Диапазон времени
            if start_time <= end_time:
                # Обычный диапазон
                if start_time <= current_time <= end_time:
                    should_send = True
            else:
                # Диапазон через полночь
                if current_time >= start_time or current_time <= end_time:
                    should_send = True

        if not should_send:
            continue

        try:
            # Параметры для отправки
            send_params = {
                'chat_id': chat['id'],
                'text': message
            }

            # Если есть thread_id, добавляем его
            if chat.get('thread_id'):
                send_params['message_thread_id'] = chat['thread_id']

            await context.bot.send_message(**send_params)
            success_count += 1

            thread_info = f" (тема: {chat['thread_id']})" if chat.get('thread_id') else ""
            print(f"[{datetime.now(TIMEZONE)}] Сообщение отправлено в {chat['title']}{thread_info} ({chat['id']})")
        except Exception as e:
            print(f"[{datetime.now(TIMEZONE)}] Ошибка отправки в {chat['title']} ({chat['id']}): {e}")
            failed_chats.append((chat['id'], chat.get('thread_id')))

    # Удаляем чаты, куда не удалось отправить
    for chat_id, thread_id in failed_chats:
        remove_chat(chat_id, thread_id)

    if success_count > 0:
        print(f"[{datetime.now(TIMEZONE)}] Отправлено в {success_count} чатов")