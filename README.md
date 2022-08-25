# Pi Bot
This open source project is a robot for the Raspberry pi platform. Boobot or Pi Bot is mainly designed to be a hobbyist playground. This project was designed to contain basic components for a robot. 

Some of the potential uses for this robot are a bluetooth speaker, mini linux PC, server with UPS and status, machine learning project, AI assistant, Steam Link reciever, retro gaming console, media player, home automation, and much more! With the inclusion of the modular SPI port on the bottom, it can connect and control other devices like a smart automatic carpet vacuum! 

![robot](/images/photo2.jpg)

## Features
- **Camera:** 5MP, 1080p
- **Microphone:** I2S MEMS microphone with a range of about 50Hz - 15KHz, good for just about all general audio recording/detection.
- **Speaker:** This small mono class D amplifier able to deliver 1.6 Watts of power into a 8 ohm impedance speaker
- **Servos:** Output for 9 separate servos. These include a 180 degree servo for the camera and 2 360 servos for the wheels.
- **Accelerometer:** 3-axis accelerometer
- **Gyroscope:** 3-axis gyroscope
- **Magnetometer:** 3-axis magnetometer
- **Barometer:** Environmental sensor with temperature, barometric pressure with ±1 meter accuracy.
- **Addressable RGB LEDs:** Three primary color can achieve 256 brightness with a refresh rate is 30fps,
- **OLED Display:** Display made of 128x64 individual white OLED pixels. Display used for notifications and AI status
- **Menu Buttons:** 4 tactile buttons. Three are used for menu navigation and the third is used for waking up from power off mode. 
- **PWM Fan:** 40mm fan with dynamic speed control
- **Modular Port:** Used to connect to 2 other devices through SPI.
- **LiPo:** 2 flat top 26650 LiPo batteries in series. Each LiPo with the capacity of 6800mAh. Buck Converter can take up to 16V but external charger is required. Batteries are swappable and have a 2S BMS system available. 
- **Current Charge Sensor:** Includes a current and voltage meter to accuratly detect if charging/discharging and current charge. 


## Initial setup
On a terminal window use the following (PLEASE USE A FRESH INSTALL OF RASBIAN TO PREVENT SOUND SYSTEM ERRORS)
```
git clone https://github.com/RetroDISTORT/boobot.git
```

## PCB
![robot](/images/PCB_3D.png)

## Circuit
![robot](/images/PCB_Wiring.png)

## Coming Soon
- 3D print files and parts list
- PCB files
