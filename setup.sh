#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Конфигурация
BOT_DIR="/opt/telegram-bot"
SERVICE_NAME="telegram-bot"
VENV_DIR="${BOT_DIR}/venv"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  Установка Telegram New Year Bot${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Ошибка: Скрипт должен быть запущен с правами root${NC}"
    echo "Используйте: sudo ./setup.sh"
    exit 1
fi

# Проверка наличия Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Ошибка: Python 3 не установлен${NC}"
    echo "Установите Python 3: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

echo -e "${YELLOW}[1/8] Создание директории для бота...${NC}"
mkdir -p "$BOT_DIR"
echo -e "${GREEN}✓ Директория создана: $BOT_DIR${NC}"
echo ""

echo -e "${YELLOW}[2/8] Копирование файлов бота...${NC}"
if [ -f "$SCRIPT_DIR/bot.py" ]; then
    cp -r "$SCRIPT_DIR/utils" "$BOT_DIR/"
    cp "$SCRIPT_DIR/bot.py" "$BOT_DIR/"
    echo -e "${GREEN}✓ Файл bot.py скопирован${NC}"
else
    echo -e "${RED}Ошибка: Файл bot.py не найден в текущей директории${NC}"
    exit 1
fi

# Копирование .env файла если существует
if [ -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env" "$BOT_DIR/.env"
    chmod 600 "$BOT_DIR/.env"
    echo -e "${GREEN}✓ Файл .env скопирован${NC}"
fi
echo ""

echo -e "${YELLOW}[3/8] Создание виртуального окружения...${NC}"
python3 -m venv "$VENV_DIR"
echo -e "${GREEN}✓ Виртуальное окружение создано${NC}"
echo ""

echo -e "${YELLOW}[4/8] Установка зависимостей...${NC}"
"$VENV_DIR/bin/pip" install --upgrade pip > /dev/null 2>&1
"$VENV_DIR/bin/pip" install python-telegram-bot pytz > /dev/null 2>&1
"$VENV_DIR/bin/pip" install "python-telegram-bot[job-queue]" > /dev/null 2>&1

# Установка python-dotenv если есть .env
if [ -f "$BOT_DIR/.env" ]; then
    "$VENV_DIR/bin/pip" install python-dotenv > /dev/null 2>&1
    echo -e "${GREEN}✓ Зависимости установлены (с python-dotenv)${NC}"
else
    echo -e "${GREEN}✓ Зависимости установлены${NC}"
fi
echo ""

echo -e "${YELLOW}[5/8] Создание пользователя для бота...${NC}"
if ! id -u telegram-bot &> /dev/null; then
    useradd -r -s /bin/false telegram-bot
    echo -e "${GREEN}✓ Пользователь telegram-bot создан${NC}"
else
    echo -e "${GREEN}✓ Пользователь telegram-bot уже существует${NC}"
fi
echo ""

echo -e "${YELLOW}[6/8] Установка прав доступа...${NC}"
chmod +x "$BOT_DIR/bot.py"
chown -R telegram-bot:telegram-bot "$BOT_DIR"
echo -e "${GREEN}✓ Права доступа установлены${NC}"
echo ""

echo -e "${YELLOW}[7/8] Создание systemd сервиса...${NC}"
cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Telegram New Year Countdown Bot
After=network.target

[Service]
Type=simple
User=telegram-bot
Group=telegram-bot
WorkingDirectory=${BOT_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/python ${BOT_DIR}/bot.py
Restart=always
RestartSec=10

# Логирование
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Systemd сервис создан${NC}"
echo ""

echo -e "${YELLOW}[8/8] Настройка и запуск сервиса...${NC}"
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

# Проверка статуса
sleep 2
if systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✓ Сервис успешно запущен и активирован${NC}"
else
    echo -e "${RED}✗ Ошибка при запуске сервиса${NC}"
    echo "Проверьте логи: sudo journalctl -u ${SERVICE_NAME} -n 50"
    exit 1
fi
echo ""

echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  Установка завершена успешно! 🎉${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "Управление сервисом:"
echo -e "  Статус:      ${YELLOW}sudo systemctl status ${SERVICE_NAME}${NC}"
echo -e "  Остановить:  ${YELLOW}sudo systemctl stop ${SERVICE_NAME}${NC}"
echo -e "  Запустить:   ${YELLOW}sudo systemctl start ${SERVICE_NAME}${NC}"
echo -e "  Перезапуск:  ${YELLOW}sudo systemctl restart ${SERVICE_NAME}${NC}"
echo ""
echo -e "Логи:"
echo -e "  Просмотр:    ${YELLOW}sudo journalctl -u ${SERVICE_NAME} -f${NC}"
echo -e "  Последние:   ${YELLOW}sudo journalctl -u ${SERVICE_NAME} -n 50${NC}"
echo ""
echo -e "Файлы бота находятся в: ${YELLOW}${BOT_DIR}${NC}"
echo ""