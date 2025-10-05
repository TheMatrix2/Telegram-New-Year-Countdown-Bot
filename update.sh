#!/bin/bash
sudo systemctl stop telegram-bot

git restore setup.sh update.sh
git pull

sudo cp bot.py /opt/telegram-bot/
sudo cp -r utils /opt/telegram-bot/

sudo systemctl start telegram-bot

sudo chmod +x setup.sh
sudo chmod +x update.sh

echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}     Update completed successfully!    ${NC}"
echo -e "${GREEN}=======================================${NC}"