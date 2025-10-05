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

    # Получаем thread_id если это сообщение в теме
    message_thread_id = update.effective_message.message_thread_id if update.effective_message.is_topic_message else None

    # Добавляем чат в список
    is_new = add_chat(chat_id, chat_type, chat_title, message_thread_id)

    # Формируем информацию о теме
    thread_info = ""
    if message_thread_id:
        topic_name = "эту тему"
        try:
            # Пытаемся получить название темы
            forum_topic = await context.bot.get_forum_topic_icon_stickers(chat_id)
            topic_name = f"тему (ID: {message_thread_id})"
        except:
            pass
        thread_info = f"\n📌 Сообщения будут отправляться в {topic_name}"

    # Логируем
    log_thread = f" [тема: {message_thread_id}]" if message_thread_id else ""
    print(
        f"[{datetime.now(TIMEZONE)}] /start от {chat_title}{log_thread} ({chat_id}, {chat_type}) - {'новый чат' if is_new else 'уже подписан'}")

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
    message_thread_id = update.effective_message.message_thread_id if update.effective_message.is_topic_message else None

    remove_chat(chat_id, message_thread_id)

    thread_info = f" [тема: {message_thread_id}]" if message_thread_id else ""
    print(f"[{datetime.now(TIMEZONE)}] /stop от {chat_title}{thread_info} ({chat_id})")

    topic_text = " из этой темы" if message_thread_id else ""
    await update.message.reply_text(
        f"😢 Вы отписались от уведомлений{topic_text}.\n\n"
        "Чтобы снова подписаться, отправьте /start"
    )


async def check_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /check - показывает актуальное количество дней"""
    message = countdown_message()

    await update.message.reply_text(message)


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /chatid - показывает ID чата и темы"""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title if hasattr(update.effective_chat, 'title') else "Личный чат"
    message_thread_id = update.effective_message.message_thread_id if update.effective_message.is_topic_message else None

    message = (
        f"📋 Информация о чате:\n\n"
        f"Chat ID: `{chat_id}`\n"
        f"Тип: {chat_type}\n"
        f"Название: {chat_title}"
    )

    if message_thread_id:
        message += f"\n\n🧵 Тема (Topic):\nThread ID: `{message_thread_id}`"
        message += f"\n\n💡 Сообщения будут отправляться именно в эту тему"

    await update.message.reply_text(message, parse_mode='Markdown')