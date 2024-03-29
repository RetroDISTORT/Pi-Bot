#!/bin/bash
echo "Starting setup..."
echo " "

# Check if code is being ran as root
if (( $EUID != 0)); then
    echo "Please run this script as root."
    exit
fi

# Move all the files to the root directory
echo "Moving files to root directory"
cp -r ../../boobot  /opt

echo "Creating profile directory .boobot"
mkdir -p ~/.boobot

read -p "apt-get update & upgrade? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Updating..."
    sudo apt-get -y update
    echo "Upgrading..."
    sudo apt-get -y upgrade
    echo " "
    echo "Update and Upgrade done "
fi
echo " "

# Install emacs
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

# Install bluetooth 
 read -p "Install bluetooth packages? Y/n... " -n 1 -r
 if [[ ! $REPLY =~ ^[Nn]$ ]]
 then
     echo " "
     echo "Installing bluez..."
     sudo apt install python3-dbus
     echo " "
     echo " installation done "
 fi
 echo " "

# Install retropie
read -p "Install Retropie? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing retropie..."
    mkdir ~/RetroPie
    git clone --depth=1 https://github.com/RetroPie/RetroPie-Setup.git ~/RetroPie
    chmod +x ~/RetroPie/retropie_setup.sh
    sudo ~/RetroPie/retropie_setup.sh
    #rm -rf retropie/
    echo " "
    echo "Retropie installation done "
fi
echo " "

# Speaker setup
read -p "Install MAX98357 I2S Speaker AMP? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing necessary drivers..."
    sudo echo "" > '/etc/modprobe.d/raspi-blacklist.conf' 
    sudo cp ./src/modules /etc/
    sudo apt-get install alsa-utils #ensure installation & update alsa-utils
    sudo cp ./srcasound.conf /etc/asound.conf
    sed -i 's/^dtparam=audio=on/#dtparam=audio=on/' /boot/config.txt
    if grep -q "dtoverlay=hifiberry-dac" "/boot/config.txt"; then
	echo "I2S overlays were edited before, re-running script?" # SomeString was found
    else
	sudo echo "" >> /boot/config.txt
	sudo echo "dtoverlay=hifiberry-dac" >> /boot/config.txt
	sudo echo "dtoverlay=i2s-mmap" >> /boot/config.txt
	echo "I2S overlays added!"
    fi
    sudo python3 -m pip install --force-reinstall adafruit-blinka # Required for board and digitalio
    echo "MAX98357 driver installation done!"
    echo "Instalation guide from:"
    echo "https://bytesnbits.co.uk/raspberry-pi-i2s-sound-output/"
fi
echo " "

# Microphone setup
read -p "Install SPH0645 I2S MIC? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing necessary drivers..."
    mkdir ./mic
    #sudo pip3 install --upgrade adafruit-python-shell
    wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/i2smic.py -P ./mic/
    sudo python3 ./mic/i2smic.py
    rm -rf ./mic
    cp ./.asoundrc ~/ #Mic volume control
    echo "SPH0645 driver installation done!"
fi
echo " "

# Oled setup
read -p "Install OLED Drivers? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing ...\n"
    echo "Installing Adafruit_GPIO ...\n"
    sudo apt-get install python3-pip
    sudo pip3 install adafruit-circuitpython-ssd1306
    sudo apt-get install python3-pil
    sudo apt-get install python3-numpy
    sudo python3 -m pip install --force-reinstall adafruit-blinka # Required for board and digitalio
    
    if grep -q "dtparam=i2c_baudrate=1000000" "/boot/config.txt"; then
	echo "i2c speed is already at 1MHz"
    else
	sudo echo "dtparam=i2c_baudrate=1000000" >> /boot/config.txt
	echo "I2C baudrate set at 1MHz"
    fi
    
    echo "OLED driver installation done!"
fi
echo " "

# Neopixels setup
read -p "Install NeoPixel Drivers? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing necessary drivers..."
    sudo pip3 install adafruit-circuitpython-NeoPixel
    sudo pip3 install adafruit-circuitpython-Pixel-Framebuf
    sudo pip3 install adafruit-circuitpython-Pixelbuf
    sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
    echo " "
    echo "Neopixels driver installation done!"
fi
echo " "

# LiPo sensor setup
read -p "Install INA219 Battery Sensor Drivers? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing necessary drivers..."
    sudo pip3 install adafruit-circuitpython-ina219
    echo "INA219 driver installation done!"
fi
echo " "

# Servo controller setup
read -p "Install PCA9685 Servo Controller? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing necessary drivers..."
    sudo pip3 install adafruit-circuitpython-pca9685
    sudo pip3 install adafruit-circuitpython-servokit
    echo "PCA9685 driver installation done!"
fi
echo " "

# Accelerometer setup
read -p "Install MPU9250 Accel/Gyro/Mag?(NOT WORKING) Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing necessary drivers..."
    #sudo pip install FaBo9Axis_MPU9250
    echo "MPU9250 driver installation done!"
fi
echo " "

# Pressure and temp sensor setup
read -p "Install BMP280 Pres/Temp Sensor? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing necessary drivers..."
    sudo pip3 install adafruit-circuitpython-bme280
    echo "BME280 driver installation done!"
fi
echo " "

# Hotspot setup
read -p "Install Hotspot? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing necessary drivers..."
    sudo apt-get -y install hostapd dnsmasq
    sudo mv ./dhcpcd.conf  /etc/dhcpcd.conf
    sudo mv ./interfaces   /etc/network/interfaces
    sudo mv ./hostapd.conf /etc/hostapd/hostapd.conf
    sudo mv ./hostapd      /etc/default/hostapd
    sudo mv /etc/dnsmasq.conf  /etc/dnsmasq.conf.bak
    sudo mv ./dnsmasq.conf /etc/dnsmasq.conf
    sudo mv /etc/dnsmasq.conf  /etc/dnsmasq.conf.bak
    echo "Hotspot installation done! (Reboot required to enable)"
fi
echo " "

# Startup script setup
read -p "Create Startup Script? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    current_user=$(who | head -n1 | awk '{print $1;}')
    echo " "
    echo "Setting up script for user $current_user..."
    #sudo cp ./rc.local /etc/rc.local
    #sudo chmod +x /etc/rc.local
    cp ./.profile ~/.profile
    echo "Script Ready! "
fi
echo " "

# read -p "Setup PulseAudio as a System Wide Service? Y/n... " -n 1 -r
# if [[ ! $REPLY =~ ^[Nn]$ ]]
# then
#     current_user=$(who | head -n1 | awk '{print $1;}')
#     echo " "
#     echo "Setting up..."
#     sudo cp ./pulseaudio.service /etc/systemd/system/pulseaudio.service
#     systemctl --system enable pulseaudio.service
#     systemctl --system start pulseaudio.service
#     sudo cp ./client.conf /etc/pulse/client.conf
#     sudo sed -i '/^pulse-access:/ s/$/root,'"$current_user"'/' /etc/group
#     echo "PulseAudio is Ready!"
# fi
# echo " "

# Python module setup
echo "The following modules may be required for proper installation and app functionallity."
echo "  [1] adafruit-python-shell       Required for I2S-mic"
echo "  [2] libasound2-dev              Required for pyalsaudio installation"
echo "  [3] pyalsaaudio                 Enables volume control through python"
echo "  [4] python3-pyaudio             "
echo "  [5] libpulse-dev  [skip]        C++ pulse lib NOT REQUIRED ANYMORE"
echo ""
read -p "Install python modules for apps? Y/n... " -n 1 -r
if [[ ! $REPLY =~ ^[Nn]$ ]]
then
    echo " "
    echo "Installing modules"
    sudo pip3 install adafruit-python-shell #Required for I2S-mic
    sudo apt-get install libasound2-dev     #Required for pyalsaudio
    sudo pip3 install pyalsaaudio           #Enables volume control through python
    sudo apt install python3-pyaudio  
    #sudo apt install libpulse-dev           #C++ pulse lib NOT REQUIRED
    sudo pip3 install pasimple              #Required for VU meter
    #sudo pip3 install PyAV
    sudo pip3 install aiortc
    sudo pip3 install aiohttp
    echo "Modules Ready! "
fi
echo " "
echo "DONE!"

###########################
## INSTALLATION TEMPLATE ##
###########################

# Install 
# read -p "Install ? Y/n... " -n 1 -r
# if [[ ! $REPLY =~ ^[Nn]$ ]]
# then
#     echo " "
#     echo "Installing ..."
    
#     echo " "
#     echo " installation done "
# fi
# echo " "
