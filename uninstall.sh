#!/bin/bash

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Конфигурация
BOT_DIR="/opt/telegram-bot"
SERVICE_NAME="telegram-bot"

echo -e "${YELLOW}=======================================${NC}"
echo -e "${YELLOW}  Удаление Telegram New Year Bot${NC}"
echo -e "${YELLOW}=======================================${NC}"
echo ""

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Ошибка: Скрипт должен быть запущен с правами root${NC}"
    echo "Используйте: sudo ./uninstall.sh"
    exit 1
fi

# Подтверждение удаления
read -p "Вы уверены, что хотите удалить бота? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Удаление отменено${NC}"
    exit 0
fi

echo -e "${YELLOW}[1/5] Остановка сервиса...${NC}"
if systemctl is-active --quiet ${SERVICE_NAME}; then
    systemctl stop ${SERVICE_NAME}
    echo -e "${GREEN}✓ Сервис остановлен${NC}"
else
    echo -e "${GREEN}✓ Сервис не запущен${NC}"
fi
echo ""

echo -e "${YELLOW}[2/5] Отключение автозапуска...${NC}"
if systemctl is-enabled --quiet ${SERVICE_NAME} 2>/dev/null; then
    systemctl disable ${SERVICE_NAME}
    echo -e "${GREEN}✓ Автозапуск отключен${NC}"
else
    echo -e "${GREEN}✓ Автозапуск не был включен${NC}"
fi
echo ""

echo -e "${YELLOW}[3/5] Удаление systemd сервиса...${NC}"
if [ -f "/etc/systemd/system/${SERVICE_NAME}.service" ]; then
    rm /etc/systemd/system/${SERVICE_NAME}.service
    systemctl daemon-reload
    echo -e "${GREEN}✓ Systemd сервис удален${NC}"
else
    echo -e "${GREEN}✓ Systemd сервис не найден${NC}"
fi
echo ""

echo -e "${YELLOW}[4/5] Удаление файлов бота...${NC}"
if [ -d "$BOT_DIR" ]; then
    rm -rf "$BOT_DIR"
    echo -e "${GREEN}✓ Директория $BOT_DIR удалена${NC}"
else
    echo -e "${GREEN}✓ Директория не найдена${NC}"
fi
echo ""

echo -e "${YELLOW}[5/5] Удаление пользователя...${NC}"
if id -u telegram-bot &> /dev/null; then
    userdel telegram-bot
    echo -e "${GREEN}✓ Пользователь telegram-bot удален${NC}"
else
    echo -e "${GREEN}✓ Пользователь не найден${NC}"
fi
echo ""

echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}  Удаление завершено успешно! ✓${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""