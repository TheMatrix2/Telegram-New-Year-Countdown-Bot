from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from utils.chats import add_chat, remove_chat, update_chat_time
from utils.messages import days_until_new_year, word_after_number, countdown_message
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

    # Добавляем чат в список с временем по умолчанию
    is_new = add_chat(chat_id, chat_type, chat_title, message_thread_id, "09:00", "09:00")

    # Формируем информацию о теме
    thread_info = ""
    if message_thread_id:
        topic_name = "эту тему"
        thread_info = f"\n📌 Сообщения будут отправляться в {topic_name}"

    # Логируем
    log_thread = f" [тема: {message_thread_id}]" if message_thread_id else ""
    print(
        f"[{datetime.now(TIMEZONE)}] /start от {chat_title}{log_thread} ({chat_id}, {chat_type}) - {'новый чат' if is_new else 'уже подписан'}")

    if is_new:
        message = (
            f"✅ Отлично! Теперь я буду отправлять сюда каждый день количество дней до Нового года.{thread_info}\n\n"
            f"Сейчас до Нового года: {days} {word_after_number(days)} 🎄\n\n"
            f"⏰ По умолчанию сообщения отправляются в 09:00\n"
            f"Изменить время: /settime\n\n"
            f"Другие команды:\n"
            f"/check - узнать количество дней прямо сейчас\n"
            f"/stop - отписаться от уведомлений\n"
            f"/chatid - узнать ID этого чата"
        )
    else:
        message = (
            f"Вы уже подписаны на уведомления! ✅{thread_info}\n\n"
            f"До Нового года: {days} {word_after_number(days)} 🎄\n\n"
            f"Команды:\n"
            f"/settime - изменить время отправки\n"
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


async def set_time_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало настройки времени"""
    keyboard = [
        [
            InlineKeyboardButton("Утро (08:00-10:00)", callback_data="time_preset_08:00-10:00"),
            InlineKeyboardButton("День (12:00-14:00)", callback_data="time_preset_12:00-14:00"),
        ],
        [
            InlineKeyboardButton("Вечер (18:00-20:00)", callback_data="time_preset_18:00-20:00"),
            InlineKeyboardButton("Ночь (22:00-00:00)", callback_data="time_preset_22:00-00:00"),
        ],
        [
            InlineKeyboardButton("⚙️ Указать свое время", callback_data="time_custom"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message_thread_id = update.effective_message.message_thread_id if update.effective_message.is_topic_message else None
    topic_text = " в эту тему" if message_thread_id else ""

    await update.message.reply_text(
        f"⏰ Выберите время отправки сообщений{topic_text}:\n\n"
        "Вы можете выбрать готовый диапазон или указать свое время.",
        reply_markup=reply_markup
    )


async def time_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки выбора времени"""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    message_thread_id = update.effective_message.message_thread_id if update.effective_message.is_topic_message else None

    if query.data.startswith("time_preset_"):
        # Готовый диапазон
        time_range = query.data.replace("time_preset_", "")
        time_start, time_end = time_range.split("-")

        # Обновляем время
        success = update_chat_time(chat_id, message_thread_id, time_start, time_end)

        if success:
            topic_text = " в эту тему" if message_thread_id else ""
            await query.edit_message_text(
                f"✅ Время установлено: {time_start} - {time_end}\n\n"
                f"Сообщения будут отправляться в случайное время в этом диапазоне{topic_text}.\n\n"
                f"Изменить время: /settime"
            )
        else:
            await query.edit_message_text(
                "❌ Сначала подпишитесь на уведомления командой /start"
            )

    elif query.data == "time_custom":
        # Пользовательское время
        topic_text = " в эту тему" if message_thread_id else ""
        await query.edit_message_text(
            f"⏰ Укажите время отправки{topic_text}:\n\n"
            "Формат: `/settime ЧЧ:ММ` для точного времени\n"
            "или `/settime ЧЧ:ММ-ЧЧ:ММ` для диапазона\n\n"
            "Примеры:\n"
            "`/settime 09:30` - отправка в 09:30\n"
            "`/settime 08:00-10:00` - случайное время с 8:00 до 10:00\n"
            "`/settime 22:00-02:00` - с 22:00 до 02:00 (через полночь)",
            parse_mode='Markdown'
        )


async def set_time_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Установка пользовательского времени"""
    if not context.args:
        await update.message.reply_text(
            "❌ Укажите время!\n\n"
            "Примеры:\n"
            "`/settime 09:30`\n"
            "`/settime 08:00-10:00`",
            parse_mode='Markdown'
        )
        return

    time_input = context.args[0]
    chat_id = update.effective_chat.id
    message_thread_id = update.effective_message.message_thread_id if update.effective_message.is_topic_message else None

    # Парсим время
    try:
        if '-' in time_input:
            # Диапазон
            time_start, time_end = time_input.split('-')
        else:
            # Точное время
            time_start = time_end = time_input

        # Проверяем формат
        for t in [time_start, time_end]:
            hour, minute = map(int, t.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Неверное время")

        # Обновляем время
        success = update_chat_time(chat_id, message_thread_id, time_start, time_end)

        if success:
            topic_text = " в эту тему" if message_thread_id else ""
            if time_start == time_end:
                await update.message.reply_text(
                    f"✅ Время установлено: {time_start}\n\n"
                    f"Сообщения будут отправляться в {time_start}{topic_text}.\n\n"
                    f"Изменить время: /settime"
                )
            else:
                await update.message.reply_text(
                    f"✅ Время установлено: {time_start} - {time_end}\n\n"
                    f"Сообщения будут отправляться в случайное время в этом диапазоне{topic_text}.\n\n"
                    f"Изменить время: /settime"
                )
        else:
            await update.message.reply_text(
                "❌ Сначала подпишитесь на уведомления командой /start"
            )

    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Неверный формат времени!\n\n"
            "Используйте формат ЧЧ:ММ\n"
            "Примеры: `09:30` или `08:00-10:00`",
            parse_mode='Markdown'
        )
