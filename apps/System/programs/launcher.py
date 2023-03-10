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


import sys              # Required for loading special modules

#sys.path.insert(1, '/opt/boobot/apps/System/components/server')
sys.path.insert(1, '/home/pi/Documents/boobot/apps/System/components/devices')
from batterySensor     import BatterySensor


SLEEP_DELAY = 200

def get_fonts(fontName):
    fontXL = ImageFont.truetype(fontName, 18)
    fontL  = ImageFont.truetype(fontName, 16)
    fontM  = ImageFont.truetype(fontName, 12)
    fontS  = ImageFont.truetype(fontName, 10)
    fontXS = ImageFont.truetype(fontName,  8)
    
    return [fontXL, fontL, fontM, fontS, fontXS]

def get_apps(dir):
    # list to store files
    appList = []
    # Iterate directory
    for file in os.listdir(dir):
        appFolder = os.path.join(dir, file)
        # check only text files
        if os.path.isdir(appFolder): #.endswith('.py'):
            nameIndex = appFolder.rindex('/')+1
            appList.append(appFolder[nameIndex:])

    #print(appList)
    return appList

def get_input():
    if GPIO.input(8) == 0:  # UP
        time.sleep(.25)
        return "UP"
            
    if GPIO.input(25) == 0: # MID
        return "SELECT"
            
    if GPIO.input(7) == 0:  # DOWN
        time.sleep(.25)
        return "DOWN"

    time.sleep(.05)
    return "NONE"
                
def start_app(device, fonts, appDirectory):
    try:
        exec(open(appDirectory).read(), globals()) #Run application
    except Exception as e:
        device.contrast(1) # Max contrast is 255
        printMessage(device, fonts[1], str(e))
        
    time.sleep(1)

def printMessage(device, inputFont, message):
    image = Image.new('1', (device.width, device.height))
    draw  = ImageDraw.Draw(image)
    speed = 10 # Larger is faster

    (font_width, font_height) = inputFont.getsize(message)
    time.sleep(.5)

    # Scroll error message
    for pos_x in range(0,-font_width,-speed):
        draw.rectangle((0, 10, device.width, device.height - 10), outline=0, fill=255)
        draw.text((pos_x , 25), message, font = inputFont, fill = 0)
        device.image(image)
        device.show()

def menu(directory, device, fonts, menu):
    timeToSleep = SLEEP_DELAY
    done = False
    draw_menu(device, fonts, menu)
    
    while(not done):
        input = ""
        while(input==""):
            input = get_input()
            timeToSleep -= 1
            if timeToSleep == 0:
                device.fill(0)
                device.show()
                timeToSleep = SLEEP_DELAY

        if (input == "UP"):
            menu.insert(0, menu.pop())
            draw_menu(device, fonts, menu)
            timeToSleep = SLEEP_DELAY

        if (input == "SELECT"):
            start_app(device, fonts, directory + menu[0] + "/" + menu[0] + ".py")
            draw_menu(device, fonts, menu)
            timeToSleep = SLEEP_DELAY

        if (input == "DOWN"):
            menu.append(menu.pop(0))
            draw_menu(device, fonts, menu)
            timeToSleep = SLEEP_DELAY

def draw_menu(device, fonts, menu):
    image = Image.new('1', (device.width, device.height))
    draw = ImageDraw.Draw(image)
    done = False
    hshift = [15,5,0,5] #[0,5,15,5,0]
    vshift = [21,37,51,1,10]#[1,10,21,37,51]
    useFont  = [1,2,4,2]#[4,2,1,2,4]
        
    draw.rectangle((0, 25, device.width, 39), outline=0, fill=255)
    for i in range(-2,3):
        if len(menu) > abs(i):
            draw.text((hshift[i] , vshift[i]), menu[i], font=fonts[useFont[i]],fill = 0 if i == 0 else 255)
                
    device.image(image)
    device.show()


def lockScreen(device, fonts):
    battery   = BatterySensor()
    image     = Image.new('1', (device.width, device.height))
    draw      = ImageDraw.Draw(image)
    time      = "9:20am"
    battery.update()
    charge    = battery.getCharge()
    battery_x = 114
    battery_y = 0

    #clock
    draw.text((15 , 21), time, font=fonts[1], fill = 255)
    #draw.text((15 , 21), "", font=fonts[3], fill = 255)

    #Battery
    print(charge)
    draw.rectangle((battery_x + 0, battery_y + 3, battery_x + 0, battery_y + 5), outline=255, fill=0)
    draw.rectangle((battery_x + 1, battery_y + 1, battery_x + 13, battery_y + 7), outline=255, fill=0)
    draw.rectangle((battery_x + 2 + int(10-charge/10), battery_y + 2 , battery_x + 12, battery_y + 6), outline=0, fill=255)


    
    
    device.image(image)
    device.show()
    

def main(directory):
    WIDTH  = 128  # DISPLAY
    HEIGHT = 64   # DISPLAY
    BORDER = 5    # DISPLAY
    
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    fontList = get_fonts('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf')
    optionList = get_apps(directory)
    
    oled.contrast(1) # Max contrast is 255

    GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
    GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) # CENTER

    lockScreen(oled, fontList)
    #menu(directory, oled, fontList, optionList)
    
if __name__ == "__main__":
    main('/opt/boobot/apps/')
