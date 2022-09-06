# Pi Bot
This open source project is a robot for the [Raspberry pi](https://www.raspberrypi.com/) platform. Boobot or Pi Bot is mainly designed to be a hobbyist playground. This project was designed to contain basic components for a robot. 

Some of the potential uses for this robot are a bluetooth speaker, mini linux PC, server with UPS and status, machine learning project, AI assistant, Steam Link reciever, retro gaming console, media player, home automation, and much more! With the inclusion of the modular SPI port on the bottom, it can connect and control other devices like a smart automatic carpet vacuum! 

This project is a continuation of [BOOBOT v0.2.0](https://github.com/Shizcow/BooBot/tree/v0.2.0). A class project designed to serve a twitch live stream and controlled by chat.

Boobot hat is compatible with the new Raspberry Pi Pinout:
Raspberry Pi B+
Raspberry Pi 2
Raspberry Pi 3
Raspberry Pi 4
Raspberry Pi Zero

![robot](/images/photo2.jpg)

## Features
- **Camera:** 5MP, 1080p at 30fps. Used for remote control, automation, security, webcam, etc. 
- **Microphone:** I2S MEMS microphone with a range of about 50Hz - 15KHz, good for just about all general audio recording/detection.
- **Speaker:** This small mono class D amplifier able to deliver 1.6 Watts of power into a 8 ohm impedance speaker. Good for playing music, videocalls, Bluetooth speaker and notifications.
- **Servos:** Output for 9 separate servos. These include a 180 degree servo for the camera and 2 360 servos for the wheels. Servos are powered through a power supply independent from rasperry pi's
- **Accelerometer:** 3-axis accelerometer. Used for collision and movement detection.
- **Gyroscope:** 3-axis gyroscope. Used to for detecting inclination and orientation.
- **Magnetometer:** 3-axis magnetometer. Used as an internal compass for diractioning and orientation.
- **Barometer:** Environmental sensor with temperature, barometric pressure with ±1 meter accuracy. Used to determine current height.
- **Addressable RGB LEDs:** Three primary color can achieve 256 brightness with a refresh rate is 30fps. Good for notifications, camera lights, and look cool overall!
- **OLED Display:** Display made of 128x64 individual white OLED pixels. Usefull for notifications and AI status.
- **Menu Buttons:** 4 tactile buttons. Three are used for menu navigation and the third is used for waking up from power off mode. 
- **PWM Fan:** 40mm fan with dynamic speed control for cooling internal components.
- **Modular Port:** Used to connect to 2 other devices through SPI.
- **LiPo:** 2 flat top 26650 LiPo batteries in series. Each LiPo with the capacity of 6800mAh. Buck Converter can take up to 16V but external charger is required. Batteries are swappable and have a 2S BMS system available.
- **Current Charge Sensor:** Includes a current and voltage meter to accuratly detect if charging/discharging and current charge. 


## Initial setup
On a terminal window use the following (PLEASE USE A FRESH INSTALL OF RASBIAN TO PREVENT SOUND SYSTEM ERRORS)
```
git clone https://github.com/RetroDISTORT/boobot.git
cd boobot
./setup.sh
```
Follow the installation options for all the available hardware on your robot.
After the instalation, open the code folder to use test the instalation.

## Files
The project contains a set of files for easy use. 
- **setup.sh:**
This script is installs all the drivers in the right order and installs special software for daemons and services.

- **code folder:**
Code folder contains code for testing all the hardware features. It also contains example code for deveopment.

- **misc folder:**
Contains files required for installation. Modifing these files can cause errors upon installation. 

## Circuit
The design was made from scratch. Cubebot only needs 3 servos, but 10 are available for flexibility in other designs. The hat board contains all the main sesnors and ports with the exception of the microphone, and barometer. The barometer and mic are placed the the front panel board for noise reduction and easy replaceability.
![robot](/images/PCB_Wiring.png)

## PCB
The PCB was designed using [EasyEDA](https://easyeda.com/) and printed through [JLCPCB](https://jlcpcb.com/). The design contains the main hat board, modular port, and the front panel board.
![robot](/images/PCB_3D.png)
 
## Coming Soon
- 3D print files and parts list
- PCB files
