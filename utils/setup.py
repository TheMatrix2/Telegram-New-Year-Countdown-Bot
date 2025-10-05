import os
import pytz

# Попытка загрузить переменные из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
    USE_ENV = True
except ImportError:
    USE_ENV = False

# Получаем конфигурацию из переменных окружения или используем значения по умолчанию
BOT_TOKEN = os.getenv("BOT_TOKEN", "BOT_TOKEN")
TIMEZONE_STR = os.getenv("TIMEZONE", "Europe/Moscow")

# Файл для хранения списка чатов
CHATS_FILE = "chats.json"

# Настройка часового пояса
try:
    TIMEZONE = pytz.timezone(TIMEZONE_STR)
except pytz.exceptions.UnknownTimeZoneError:
    print(f"Предупреждение: Неизвестный часовой пояс '{TIMEZONE_STR}', используется Europe/Moscow")
    TIMEZONE = pytz.timezone('Europe/Moscow')