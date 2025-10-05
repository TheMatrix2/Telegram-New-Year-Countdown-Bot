from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from utils.chats import add_chat, days_until_new_year, remove_chat
from utils.messages import word_after_number, countdown_message
from utils.setup import TIMEZONE


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
            f"Сейчас до Нового года: {days} {word_after_number(days)} 🎄\n\n"
            f"Команды:\n"
            f"/check - узнать количество дней прямо сейчас\n"
            f"/stop - отписаться от уведомлений\n"
            f"/chatid - узнать ID этого чата"
        )
    else:
        message = (
            f"Вы уже подписаны на уведомления! ✅\n\n"
            f"До Нового года: {days} {word_after_number(days)} 🎄\n\n"
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