import time             # Required for delays
import board            # Required for I2C bus
import busio            # Required for I2C bus
import digitalio        # Required for I2C bus

import adafruit_ssd1306 # Required for OLED displays
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

from PIL import Image, ImageDraw, ImageFont


class Canvas:
    def __init__(self, fontDir='/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', size=12, contrast=1):
        self.scrollSpeed = 1
        self.minGraph    = 0
        self.maxGraph    = 1

        self.font        = ImageFont.truetype(fontDir, size)
        self.i2c         = busio.I2C(board.SCL, board.SDA)
        self.display     = adafruit_ssd1306.SSD1306_I2C(128, 64, self.i2c, addr=0x3c)
        self.image       = Image.new('1', (self.display.width, self.display.height))
        self.draw        = ImageDraw.Draw(self.image)
        self.array       = []
        
        self.display.contrast(contrast)        


    def loadFont(self, fontDir, size):
        return ImageFont.truetype(fontDir, size)
        
        
    def setFont(self, font):
        self.font = font
        

    def mapValueExt(self, value, fromMinimum, fromMaximum, toMinimum, toMaximum):
        value = max(fromMinimum,min(fromMaximum,value))
        if value==fromMaximum:
            return toMaximum #Rounding in the last line may cause it to return a greater value
        if value==fromMinimum:
            return toMinimum
        
        inMax     = abs(fromMinimum-fromMaximum)
        outMax    = abs(toMinimum-toMaximum)
        newValue  = value - fromMinimum 
        output    = 0 if inMax==0 else (newValue*outMax/inMax)+toMinimum
        
        return max(toMinimum,min(toMaximum,output))
        

    def mapValue(self, value, minimum, maximum):
        maxDif = 1 if minimum==maximum else abs(minimum-maximum) # distance between min and max
        curDif = abs(minimum-value)
        
        return curDif / maxDif * 100


    def addText(self, x, y, text, fill=255, font=None):
        self.draw.text((x , y), text, font=self.font if font==None else font , anchor='rm', fill=fill)


    def addRectangle(self, x, y, w, h, outline=255, fill=0):
        self.draw.rectangle((x, y, x+w, y+h), outline=outline, fill=fill)


    def addLine(self, x, y, w, h, width=1, fill=255):
        self.draw.line((x, y, x+w, y+h), width=width, fill=fill)


    def addPoint(self, x, y, fill=255):
        self.draw.point((x,y), fill)


    def addEllipse(self, x, y, w, h, fill=255):
        self.draw.point((x, y, w, h), fill)

        
    def drawCanvas(self, clear=True):
        self.display.image(self.image)
        self.display.show()
        if clear:
            self.clear()
    
        
    def addGraph(self, x, y, graphWidth, graphHeight, array):
        self.maxGraph = max(array)
        self.minGraph = min(array)
        
        for i in range(len(array)-1):
            point1Y = (y+graphHeight) - self.mapValueExt(array[i],   self.minGraph, self.maxGraph, 0, graphHeight)
            point1X = self.mapValueExt(i, 0, len(array), x, x+graphWidth)
            point2Y = (y+graphHeight) - self.mapValueExt(array[i+1], self.minGraph, self.maxGraph, 0, graphHeight)
            point2X = self.mapValueExt(i+1, 0, len(array), x, x+graphWidth)
            self.draw.line((point1X, point1Y, point2X, point2Y), width=0, fill=255)     # Voltage Line


    def clear(self):
        self.draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0)

        
    def displayOff(self):
        self.draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0)
        self.display.image(self.image)
        self.display.show()
