import board
import busio
import adafruit_ssd1306
import digitalio
import random
import time
from PIL import Image, ImageDraw, ImageFont


def open(device, draw, image):
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    device.image(image)
    device.show()

def close(device, draw, image):
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    draw.rectangle((0, 0, device.width, 30), outline=0, fill=0) #Top
    draw.rectangle((0, device.height, device.width, 34), outline=0, fill=0) #Bottom
    device.image(image)
    device.show()
    
def annoyed(device, draw, image):
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    draw.rectangle((0, 0, device.width, 30), outline=0, fill=0) #Top
    device.image(image)
    device.show()
    
def happy(device, draw, image):
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    draw.rectangle((0, device.height, device.width, 34), outline=0, fill=0) #Bottom
    device.image(image)
    device.show()
    
def confused_right(device, draw, image):
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    draw.rectangle((0, 0, device.width/2, 30), outline=0, fill=0) #Top
    device.image(image)
    device.show()
    
def confused_left(device, draw, image):
    draw.rectangle((0, 0, device.width, device.height), outline=0, fill=0)
    draw.ellipse((9,9,55,55), fill=255)
    draw.ellipse((73,9,119,55), fill=255)
    draw.rectangle((device.width/2, 0, device.width, 30), outline=0, fill=0) #Top
    device.image(image)
    device.show()

def main():
    WIDTH = 128
    HEIGHT = 64
    BORDER = 0

    time.sleep(2)
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    oled.contrast(1)
    image = Image.new('1', (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    open(oled, draw, image)
    while(True):
    
        time.sleep(random.randint(3, 20))
        random_number = random.randint(1, 6)

        close(oled, draw, image)
        time.sleep(.5) #Blink before changing
    
        if (random_number == 1):
            open(oled, draw, image)
        if (random_number == 2):
            close(oled, draw, image)
        if (random_number == 3):
            annoyed(oled, draw, image)
        if (random_number == 4):
            happy(oled, draw, image)
        if (random_number == 5):
            confused_right(oled, draw, image)
        if (random_number == 6):
            confused_left(oled, draw, image)
            

if __name__ == "__main__":
    main()
