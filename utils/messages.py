from datetime import datetime
from telegram.ext import ContextTypes
import random

from utils.chats import load_chats, remove_chat, generate_random_time, save_chats
from utils.setup import TIMEZONE

EMOJIS = [
    "🎄", "⏰", "📅", "🎅", "❄️", "⭐", "🔔", "🎁", "✨", "🎆", "🎇", "☃️", "⛄", "🌨️", "🧣",
    "🧤", "💫", "🌠", "🦌", "🍾", "🥂", "🍷", "🍻", "🍸", "🍰", "🎂", "🍪", "🌲", "💐", "🌙", "💥", "🔥",
]

MESSAGE_TEMPLATES = [
    "Осталось всего {days} {word} до Нового года!", "До Нового года {days} {word}!", "Новый год через {days} {word}!",
    "До НГ осталось {days} {word}!", "Ещё {days} {word} до волшебства!", "Всего {days} {word} до праздника!",
    "{days} {word} до мандаринов и оливье!", "На календаре {days} {word} до Нового года!",
    "До праздника {days} {word}!", "Новогодняя ночь через {days} {word}!",
    "{days} {word} до самой волшебной ночи!", "Осталось {days} {word} до чудес!", "{days} {word} и начнется волшебство!",
    "До боя курантов {days} {word}!", "Ещё {days} {word} – и Новый год!", "{days} {word} до исполнения желаний!",
    "До главной ночи года {days} {word}!", "{days} {word} до новогоднего волшебства!", "Считаем дни: {days} {word} до НГ!",
    "{days} {word} до шампанского и салюта!", "{days} {word} до Нового года – время летит!",
    "Новый год уже близко: {days} {word}!",
    "{days} {word} до того самого боя курантов!", "{days} {word} и наступит волшебство!",
    "До новогодних чудес {days} {word}!", "Осталось подождать {days} {word}!",
    "{days} {word} до самой яркой ночи года!", "До новых надежд и мечтаний {days} {word}!", "{days} {word} до новых начинаний!",
    "Новый год придёт через {days} {word}!", "{days} {word} до ёлки и гирлянд!", "До сказки осталось {days} {word}!",
    "{days} {word} – скоро праздник!", "Ждём Новый год: {days} {word}!", "{days} {word} до снега и подарков!",
    "До загадывания желаний {days} {word}!", "{days} {word} – готовься к чуду!", "Новогодняя магия через {days} {word}!",
    "{days} {word} до самого долгожданного праздника!", "До зимней сказки {days} {word}!", "{days} {word} – и начнется новая глава!",
    "Осталось {days} {word} до огней и радости!", "{days} {word} до новогоднего настроения!", "До праздничного настроения {days} {word}!",
    "{days} {word} – время верить в чудеса!", "До встречи с чудом {days} {word}!", "{days} {word} и всё станет волшебным!",
]

MEME_MESSAGES = {
    100: "💯 СТО ДНЕЙ! Паника! Паника! ПАНИКА! 🚨",
    99: "🎯 99 проблем, но до НГ не одна из них! Осталось 99 дней! 🎸",
    69: "😏 Nice. Осталось 69 дней до Нового года!",
    42: "🤖 42 дня – ответ на главный вопрос о жизни, вселенной и Новом годе!",
    31: "📆 Последний месяц! 31 день до волшебства!",
    21: "🎓 21 день – говорят, за это время вырабатывается привычка!",
    14: "💝 Две недели! 14 дней до Нового года!",
    10: "🔟 ДЕСЯТЬ ДНЕЙ! Начинаем реальную подготовку! 🎄",
    7: "📅 Неделя! Семь дней до Нового года! Время действовать! 🏃",
    5: "🖐️ Пять дней! Можно пересчитать на пальцах!",
    3: "3️⃣ ТРИ ДНЯ! Елка куплена? Оливье готово? ПАНИКА! 😱",
    2: "2️⃣ ПОСЛЕЗАВТРА! Два дня до Нового года! 🎊",
    1: "1️⃣ ЗАВТРА! Один день! 24 часа! 1440 минут! ЭТО СЛУЧИТСЯ! 🎉🎉🎉",
}

FINAL_COUNTDOWN = {
    0: "🎆🎇 С НОВЫМ ГОДОМ!!! 🎇🎆\n🥂 Пусть сбудутся все мечты! ✨"
}


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

    return f'{random.choice(EMOJIS)} {random.choice(MESSAGE_TEMPLATES).format(days=days, word=word)} {random.choice(EMOJIS)}'


def countdown_message_schedule():
    """Создает сообщение для отправки по расписанию"""
    days = days_until_new_year()

    if days in FINAL_COUNTDOWN:
        return FINAL_COUNTDOWN[days]
    if days in MEME_MESSAGES:
        return MEME_MESSAGES[days]

    word = word_after_number(days)

    funny_additions = open('utils/additions.txt').readlines()

    template = random.choice(MESSAGE_TEMPLATES)
    template = f'{random.choice(EMOJIS)} {template.format(days=days, word=word)} {random.choice(EMOJIS)}'
    addition = f'{random.choice(EMOJIS)} {random.choice(funny_additions).replace('\n', '')} {random.choice(EMOJIS)}'
    message = template + '\n' + addition

    return message


async def send_daily_message(context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ежедневное сообщение с количеством дней до НГ во все чаты"""
    message = countdown_message_schedule()

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

        if not send_time:
            time_start = chat.get('time_start', '09:00')
            time_end = chat.get('time_end', '09:00')
            send_time = generate_random_time(time_start, time_end)
            chat['random_time'] = send_time
            updated = True

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