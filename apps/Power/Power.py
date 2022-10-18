import os               # Required for running command line functions
import glob             # Required for showing applicaitons
import time             # Required for delays
import board            # Required for I2C bus
import busio            # Required for I2C bus
import random
import digitalio        # Required for I2C bus
import adafruit_ssd1306 # Required for OLED displays

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

from PIL import Image, ImageDraw, ImageFont

def main():
    WIDTH  = 128  # DISPLAY
    HEIGHT = 64   # DISPLAY
    BORDER = 5    # DISPLAY
    
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    #fontList = get_fonts('/home/retro/Documents/github/boobot/fonts/ratchet-clank-psp.ttf')
    
    oled.contrast(1) # Max contrast is 255

    GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
    GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) # CENTER

    oled.fill(0)
    oled.show()
    os.system("sudo shutdown now")
    
if __name__ == "__main__":
    main()
