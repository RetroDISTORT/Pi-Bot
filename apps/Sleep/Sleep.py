import time
import board
import busio
import adafruit_ssd1306
import digitalio

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

from PIL import Image, ImageDraw, ImageFont


def main():
    WIDTH = 128
    HEIGHT = 64
    BORDER = 0
    
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)

    oled.contrast(1) # Max contrast is 255
    
    GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
    GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) # CENTER
    
    oled.fill(0)
    oled.show()


    time.sleep(1)
    
    done = False
    
    while(not done):
        done = done or GPIO.input(7)  == 0 # DOWN
        done = done or GPIO.input(8)  == 0 # UP
        done = done or GPIO.input(25) == 0 # CENTER

    time.sleep(.1)
        
if __name__ == "__main__":
    main()
