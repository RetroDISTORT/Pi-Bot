import os
import board
import busio
import adafruit_ssd1306

from PIL import Image, ImageDraw, ImageFont


class NotificationDisplay:
    def __init__(self):
        self.width         = 128
        self.height        = 64
        self.contrast      = 1
        self.font          = None
        self.scrollSpeed   = 2
        self.i2c           = busio.I2C(board.SCL, board.SDA)
        self.display       = adafruit_ssd1306.SSD1306_I2C(self.width, self.height, self.i2c, addr=0x3c)
        self.image         = Image.new('1', (self.width, self.height))
        self.draw          = ImageDraw.Draw(self.image)

        self.get_font('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', 12)
        self.display.contrast(self.contrast)

        
    def get_font(self, directory, size):
        self.font = ImageFont.truetype(directory, size)

        
    def setFontsDirectory(self, directory):
        self.fontDirectory = directory


    def showMessage(self, message):
        (fontWidth, fontHeight) = self.font.getsize(message)
        start = 0 if fontWidth < self.width else self.width
        end   = 1 if fontWidth < self.width else -fontWidth
        step  = 1 if fontWidth < self.width else -self.scrollSpeed
            
        for pos_x in range(start, end, step):
            self.draw.rectangle((0, 10, self.width, self.height - 10), outline=0, fill=0)
            self.draw.text((pos_x , 25), message, font = self.font, fill = 255)
            self.display.image(self.image)
            self.display.show()
            
            
    def clear(self):
        self.draw.rectangle((0, 25, device.width, 39), outline=0, fill=255)
