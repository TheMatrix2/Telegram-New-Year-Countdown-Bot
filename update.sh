#!/bin/bash
sudo systemctl stop telegram-bot

cd telegram-ny-bot
git pull

sudo cp bot.py /opt/telegram-bot/

sudo systemctl start telegram-bot

echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}     Update completed successfully!    ${NC}"
echo -e "${GREEN}=======================================${NC}"