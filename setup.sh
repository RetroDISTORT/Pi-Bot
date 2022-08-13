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
    echo ""
    mkdir ./files/OLED
    echo "Installing Adafruit_GPIO ...\n"
    echo ""
    sudo apt-get install python3-pip
    sudo pip3 install adafruit-circuitpython-ssd1306
    sudo apt-get install python3-pil
    sudo apt-get install python3-numpy
    sudo python3 -m pip install --force-reinstall adafruit-blinka
    echo "OLED Drivers installation done!"
fi
echo " "
read -p "Create Startup Script? Y/n... " -n 1 -r
echo " "
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo "Setting up Script..."
    sudo cp ./code/rc.local /etc/rc.local
    echo "Script Ready! "
fi
echo " "
echo "DONE!"
