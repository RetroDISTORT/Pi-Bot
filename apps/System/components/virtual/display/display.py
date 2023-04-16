import time             # Required for delays
import board            # Required for I2C bus
import busio            # Required for I2C bus
import digitalio        # Required for I2C bus

import adafruit_ssd1306 # Required for OLED displays
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

from PIL import Image, ImageDraw, ImageFont


class Display:
    def __init__(self, font, size, contrast=1, delay=.25, sleep=200):
        self.font        = ImageFont.truetype(font, size)
        self.i2c         = busio.I2C(board.SCL, board.SDA)
        self.display     = adafruit_ssd1306.SSD1306_I2C(128, 64, self.i2c, addr=0x3c)
        self.image       = Image.new('1', (self.display.width, self.display.height))
        self.draw        = ImageDraw.Draw(self.image)
        
        self.display.contrast(contrast)
