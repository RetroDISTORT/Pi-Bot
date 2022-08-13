#!/bin/bash
echo "Starting setup..."
echo "Creating Files directory"
mkdir ./files
read -p "Install Emacs? Y/n... " -n 1 -r
echo " "
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo "Installing emacs..."
    sudo apt-get install emacs
    echo "Emacs installation done "
fi
echo " "
read -p "Install OLED Drivers? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo "Installing ...\n"
    mkdir ./files/OLED
    echo "Installing Adafruit_GPIO ...\n"
    pip3 install Adafruit_GPIO
    git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git ./files/OLED
    echo "OLED Drivers installation done!"
fi
echo " "
echo "DONE!"
