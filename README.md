# 🎄 Telegram New Year Countdown Bot

Telegram-бот, который ежедневно отправляет количество дней, оставшихся до Нового года.

## ✨ Возможности

- 📅 Ежедневная автоматическая отправка сообщения в указанное время
- 🤖 Команды для взаимодействия с ботом
- 🔄 Автоматический перезапуск при сбоях
- 📝 Логирование всех событий
- 🚀 Простая установка одной командой

## 📋 Требования

- Ubuntu 18.04+ (или другой Linux с systemd)
- Python 3.7+
- Права root для установки

## 🚀 Быстрый старт

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/yourusername/Telegram-New-Year-Countdown-Bot.git
cd Telegram-New-Year-Countdown-Bot
```

### 2. Настройте бота

Отредактируйте файл `bot.py` и укажите:
- `BOT_TOKEN` - токен от @BotFather
- `TIMEZONE` - ваш часовой пояс (по умолчанию Moscow)

**Или** создайте файл `.env`:
```bash
nano .env
```

Добавьте:
```
BOT_TOKEN=ваш_токен_от_BotFather
```

### 3. Запустите установку

```bash
chmod +x setup.sh
sudo ./setup.sh
```

Готово! Бот установлен и запущен как системный сервис.

## 📖 Как получить токен

1. Найдите @BotFather в Telegram
2. Отправьте `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен

## 🎮 Команды бота

- `/start` - Приветствие и информация о боте
- `/check` - Узнать количество дней до Нового года прямо сейчас

## ⚙️ Управление сервисом

```bash
# Проверить статус
sudo systemctl status telegram-bot

# Остановить бота
sudo systemctl stop telegram-bot

# Запустить бота
sudo systemctl start telegram-bot

# Перезапустить бота
sudo systemctl restart telegram-bot

# Просмотр логов в реальном времени
sudo journalctl -u telegram-bot -f

# Последние 50 строк логов
sudo journalctl -u telegram-bot -n 50
```

## 🔧 Обновление бота

```bash
# Остановите бота
sudo systemctl stop telegram-bot

# Обновите код
cd telegram-ny-bot
git pull

# Скопируйте новую версию
sudo cp bot.py /opt/telegram-bot/

# Запустите снова
sudo systemctl start telegram-bot
```

## 🗑️ Удаление

```bash
chmod +x uninstall.sh
sudo ./uninstall.sh
```

Скрипт удалит:
- Системный сервис
- Все файлы бота
- Пользователя telegram-bot
- Виртуальное окружение

## 📁 Структура проекта

```
telegram-ny-bot/
├── bot.py           # Основной код бота
├── setup.sh         # Скрипт установки
├── uninstall.sh     # Скрипт удаления
├── .env.example     # Пример файла с переменными
└── README.md        # Документация
```

## 🔒 Безопасность

- Бот работает от отдельного пользователя `telegram-bot` с минимальными правами
- Токен можно хранить в `.env` файле с правами 600
- Все логи доступны через systemd journal

## 🐛 Устранение неполадок

### Бот не запускается

```bash
# Проверьте логи на ошибки
sudo journalctl -u telegram-bot -n 50

# Проверьте статус
sudo systemctl status telegram-bot

# Попробуйте запустить вручную для проверки
sudo -u telegram-bot /opt/telegram-bot/venv/bin/python /opt/telegram-bot/bot.py
```

### Бот не отправляет сообщения

1. Проверьте правильность `BOT_TOKEN`
2. Убедитесь, что вы отправили боту команду `/start` в Telegram
3. Проверьте логи на ошибки

### Изменение времени отправки

Отредактируйте в `bot.py`:
```python
job_queue.run_daily(
    send_daily_message,
    time=time(hour=9, minute=0, tzinfo=TIMEZONE),  # Измените время здесь
    name="daily_countdown"
)
```

Затем перезапустите: `sudo systemctl restart telegram-bot`
