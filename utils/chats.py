import json
from datetime import datetime

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


def add_chat(chat_id, chat_type, chat_title, message_thread_id=None):
    """Добавляет чат в список, если его там нет"""
    chats = load_chats()

    # Проверяем, есть ли уже этот чат
    for chat in chats:
        if chat['id'] == chat_id and chat.get('thread_id') == message_thread_id:
            return False

    # Добавляем новый чат
    chat_data = {
        'id': chat_id,
        'type': chat_type,
        'title': chat_title,
        'added_at': datetime.now(TIMEZONE).isoformat()
    }

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


def days_until_new_year():
    """Подсчитывает количество дней до Нового года"""
    now = datetime.now(TIMEZONE)
    current_year = now.year

    # Если сегодня 31 декабря, показываем 0 дней
    new_year = datetime(current_year + 1, 1, 1, tzinfo=TIMEZONE)

    days_left = (new_year.date() - now.date()).days
    return days_left