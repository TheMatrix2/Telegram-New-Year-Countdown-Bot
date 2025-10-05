import json
import random
from datetime import datetime, time

from utils.setup import TIMEZONE, CHATS_FILE


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


def add_chat(chat_id, chat_type, chat_title, message_thread_id=None, time_start="09:00", time_end="09:00"):
    """Добавляет чат в список, если его там нет"""
    chats = load_chats()

    # Проверяем, есть ли уже этот чат с этой темой
    for chat in chats:
        if chat['id'] == chat_id and chat.get('thread_id') == message_thread_id:
            # Обновляем время если чат уже есть
            chat['time_start'] = time_start
            chat['time_end'] = time_end
            save_chats(chats)
            return False

    # Добавляем новый чат
    chat_data = {
        'id': chat_id,
        'type': chat_type,
        'title': chat_title,
        'time_start': time_start,
        'time_end': time_end,
        'added_at': datetime.now(TIMEZONE).isoformat()
    }

    # Добавляем thread_id если есть
    if message_thread_id:
        chat_data['thread_id'] = message_thread_id

    chats.append(chat_data)
    save_chats(chats)
    return True


def remove_chat(chat_id, message_thread_id=None):
    """Удаляет чат из списка"""
    chats = load_chats()
    chats = [
        chat for chat in chats
        if not (chat['id'] == chat_id and chat.get('thread_id') == message_thread_id)
    ]
    save_chats(chats)


def update_chat_time(chat_id, message_thread_id, time_start, time_end):
    """Обновляет время отправки для чата"""
    chats = load_chats()

    for chat in chats:
        if chat['id'] == chat_id and chat.get('thread_id') == message_thread_id:
            chat['time_start'] = time_start
            chat['time_end'] = time_end
            save_chats(chats)
            return True
    return False


def get_random_time_in_range(time_start_str, time_end_str):
    """Возвращает случайное время в диапазоне"""
    start_hour, start_min = map(int, time_start_str.split(':'))
    end_hour, end_min = map(int, time_end_str.split(':'))

    # Если время одинаковое, возвращаем его
    if time_start_str == time_end_str:
        return time(hour=start_hour, minute=start_min, tzinfo=TIMEZONE)

    # Преобразуем в минуты от начала дня
    start_minutes = start_hour * 60 + start_min
    end_minutes = end_hour * 60 + end_min

    # Если конец раньше начала, значит диапазон через полночь
    if end_minutes < start_minutes:
        end_minutes += 24 * 60

    # Случайное время в диапазоне
    random_minutes = random.randint(start_minutes, end_minutes)
    random_minutes = random_minutes % (24 * 60)  # Нормализуем если перешли через полночь

    random_hour = random_minutes // 60
    random_min = random_minutes % 60

    return time(hour=random_hour, minute=random_min, tzinfo=TIMEZONE)
