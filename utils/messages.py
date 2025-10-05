from datetime import datetime
from telegram.ext import ContextTypes

from utils.chats import days_until_new_year, load_chats, remove_chat
from utils.setup import TIMEZONE


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