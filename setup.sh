#!/bin/bash
echo "Starting setup..."
echo " "
echo "Creating files directory"
mkdir ./files
read -p "Install Emacs? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing emacs..."
    sudo apt-get install emacs
    echo " "
    echo "Emacs installation done "
fi
echo " "
read -p "Install OLED Drivers? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing ...\n"
    echo " "
    mkdir ./files/OLED
    echo "Installing Adafruit_GPIO ...\n"
    echo " "
    sudo apt-get install python3-pip
    sudo pip3 install adafruit-circuitpython-ssd1306
    sudo apt-get install python3-pil
    sudo apt-get install python3-numpy
    sudo python3 -m pip install --force-reinstall adafruit-blinka
    echo "OLED driver installation done!"
fi
echo " "
read -p "Install NeoPixel Drivers? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing necessary drivers..."
    sudo pip3 install adafruit-circuitpython-NeoPixel
    sudo pip3 install adafruit-circuitpython-Pixel-Framebuf
    sudo pip3 install adafruit-circuitpython-Pixelbuf
    sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
    sudo cp ./code/snd-blacklist.conf /etc/modprobe.d/snd-blacklist.conf
    echo " "
    echo "Note snd_bcm2835 has been blacklisted!"
    echo " "
    echo "Neopixels driver installation done!"
    
fi
echo " "
read -p "Create Startup Script? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Setting up Script..."
    sudo cp ./code/rc.local /etc/rc.local
    sudo chmod +x /etc/rc.local
    echo "Script Ready! "
fi
echo " "
echo "DONE!"
