from datetime import datetime, time
from telegram.ext import ContextTypes

from utils.chats import load_chats, remove_chat, generate_random_time, save_chats
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
    current_time = datetime.now(TIMEZONE)
    current_time_str = current_time.strftime("%H:%M")
    today_date = current_time.date().isoformat()
    success_count = 0
    failed_chats = []
    updated = False

    for chat in chats:
        # Проверяем, не отправляли ли уже сегодня
        if chat.get('last_sent_date') == today_date:
            continue

        # Получаем время отправки для этого чата
        send_time = chat.get('random_time', '09:00')

        # Проверяем, совпадает ли текущее время с временем отправки (с точностью до минуты)
        if send_time != current_time_str:
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

            # Обновляем дату последней отправки
            chat['last_sent_date'] = today_date

            # Генерируем новое случайное время на завтра
            time_start = chat.get('time_start', '09:00')
            time_end = chat.get('time_end', '09:00')
            chat['random_time'] = generate_random_time(time_start, time_end)

            updated = True

            thread_info = f" (тема: {chat['thread_id']})" if chat.get('thread_id') else ""
            next_time_info = f", следующая отправка в {chat['random_time']}" if time_start != time_end else ""
            print(
                f"[{current_time}] Сообщение отправлено в {chat['title']}{thread_info} ({chat['id']}){next_time_info}")
        except Exception as e:
            print(f"[{current_time}] Ошибка отправки в {chat['title']} ({chat['id']}): {e}")
            failed_chats.append((chat['id'], chat.get('thread_id')))

    # Сохраняем изменения если были отправки
    if updated:
        save_chats(chats)

    # Удаляем чаты, куда не удалось отправить
    for chat_id, thread_id in failed_chats:
        remove_chat(chat_id, thread_id)

    if success_count > 0:
        print(f"[{current_time}] Отправлено в {success_count} чатов")