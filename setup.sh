#!/bin/bash
echo "Starting setup..."
read -p "Install Emacs? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo "Installing emacs..."
    sudo apt-get install emacs
    echo "Emacs installation done "
fi
read -p "Install OLED Drivers? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo "Installing ..."
    git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
    echo "Emacs installation done "
fi
echo "DONE!"
