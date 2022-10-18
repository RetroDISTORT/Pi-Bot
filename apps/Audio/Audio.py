import os               # Required for running command line functions
import time             # Required for delays
import board            # Required for I2C bus
import busio            # Required for I2C bus
import digitalio        # Required for I2C bus
import alsaaudio        # Setting volume
import adafruit_ssd1306 # Required for OLED displays

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

from PIL import Image, ImageDraw, ImageFont

MIN_VOL  = 0
MAX_VOL  = 90
CHANGE   = 5

def get_fonts(fontName):
    fontXXL = ImageFont.truetype(fontName, 32)
    fontXL  = ImageFont.truetype(fontName, 18)
    fontL   = ImageFont.truetype(fontName, 16)
    fontM   = ImageFont.truetype(fontName, 12)
    fontS   = ImageFont.truetype(fontName, 10)
    fontXS  = ImageFont.truetype(fontName,  8)
    
    return [fontXXL, fontXL, fontL, fontM, fontS, fontXS]

def display_volume(display, sound, fonts):
    volume = sound.getvolume()
    volBar = volume[0]*(display.height-4)//MAX_VOL
    image  = Image.new('1', (display.width, display.height))
    draw   = ImageDraw.Draw(image)

    volBarBottom = display.height-2

    # Status
    draw.text((20 , 0), str(volume[0])+"%", font=fonts[0], fill = 255)
    draw.text((20 , 40), "set with ^ and v", font=fonts[3], fill = 255)
    draw.text((20 , 50), "Square to exit", font=fonts[3], fill = 255)
    if (volume[0]==MAX_VOL):
        draw.text((80 , 10), "MAX!", font=fonts[2], fill = 255)
    if (volume[0]==MIN_VOL):
        draw.text((80 , 10), "MUTE", font=fonts[2], fill = 255)
    

    # Volume Bar
    draw.rectangle((5, 2, 15, volBarBottom), outline=1, fill=0) # Volume Frame
    draw.rectangle((5, volBarBottom-volBar, 15, volBarBottom), outline=1, fill=255) # Volume Level
        
    display.image(image)
    display.show()
    

def set_volume(display, sound, fonts):
    done        = False
    display_volume(display, sound, fonts)
    
    while(not done):
        if GPIO.input(8) == 0:  # UP
            time.sleep(.1)
            volume = sound.getvolume()
            if (volume[0]<MAX_VOL):
                sound.setvolume(volume[0]+CHANGE)
                display_volume(display, sound, fonts)
            
        if GPIO.input(25) == 0: # MID
            time.sleep(.1)
            display.fill(0)
            display.show()
            done = True
            
        if GPIO.input(7) == 0:  # DOWN
            time.sleep(.1)
            volume = sound.getvolume()
            if(volume[0]>MIN_VOL):
                sound.setvolume(volume[0]-CHANGE)
                display_volume(display, sound, fonts)

def main(directory):
    WIDTH  = 128  # DISPLAY
    HEIGHT = 64   # DISPLAY
    BORDER = 5    # DISPLAY
    
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    snd = alsaaudio.Mixer()

    fontList = get_fonts(r'/opt/boobot/fonts/ratchet-clank-psp.ttf')
    
    oled.contrast(1) # Max contrast is 255
    
    GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
    GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) # CENTER
        
    set_volume(oled, snd, fontList)

    

if __name__ == "__main__":
    main(r'/opt/boobot/code/')
