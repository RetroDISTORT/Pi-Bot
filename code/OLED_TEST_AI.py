import board
import busio
import adafruit_ssd1306
import digitalio
import random
import time
from PIL import Image, ImageDraw, ImageFont

import socket

WIDTH = 128
HEIGHT = 64
BORDER = 0

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
oled.contrast(1)
image = Image.new('1', (oled.width, oled.height))
draw = ImageDraw.Draw(image)

def open():
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    oled.image(image)
    oled.show()

def close():
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    draw.rectangle((0, 0, oled.width, 30), outline=0, fill=0) #Top                                                          
    draw.rectangle((0, oled.height, oled.width, 34), outline=0, fill=0) #Bottom                                             
    oled.image(image)
    oled.show()

def annoyed():
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    draw.rectangle((0, 0, oled.width, 30), outline=0, fill=0) #Top                                                          
    oled.image(image)
    oled.show()

def happy():
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    draw.rectangle((0, oled.height, oled.width, 34), outline=0, fill=0) #Bottom                                             
    oled.image(image)
    oled.show()

def confused_right():
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    draw.rectangle((0, 0, oled.width/2, 30), outline=0, fill=0) #Top                                                        
    oled.image(image)
    oled.show()

def confused_left():
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    draw.rectangle((oled.width/2, 0, oled.width, 30), outline=0, fill=0) #Top                                               
    oled.image(image)
    oled.show()

while(True):

    time.sleep(random.randint(3, 20))
    random_number = random.randint(1, 6)

    close()
    time.sleep(.5) #Blink before changing                                                                                   

    if (random_number == 1):
        open()
    if (random_number == 2):
        close()
    if (random_number == 3):
	annoyed()
    if (random_number == 4):
	happy()
    if (random_number == 5):
        confused_right()
    if (random_number == 6):
        confused_left()
