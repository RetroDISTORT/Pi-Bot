import time             # Required for delays
import board            # Required for I2C bus
import busio            # Required for I2C bus
import digitalio        # Required for I2C bus

import adafruit_ssd1306 # Required for OLED displays
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

from PIL import Image, ImageDraw, ImageFont


class Menu:
    def __init__(self, fontDir='/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', size=12, contrast=1, delay=.25, sleep=200):
        self.hshift      = [10,5,5,5]#[15,5,0,5]      #[0,5,15,5,0]
        self.vshift      = [25,38,50,1,12] #[21,37,51,1,10]
        self.delay       = delay
        self.scrollSpeed = 1
        self.sleep       = sleep

        self.font        = ImageFont.truetype(fontDir, size)
        self.i2c         = busio.I2C(board.SCL, board.SDA)
        self.display     = adafruit_ssd1306.SSD1306_I2C(128, 64, self.i2c, addr=0x3c)
        self.image       = Image.new('1', (self.display.width, self.display.height))
        self.draw        = ImageDraw.Draw(self.image)
        
        self.display.contrast(contrast)        
        

    def displayMenuClear(self):
        self.prevOptions = None


    def setGPIO(self):
        GPIO.setup(7,  GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
        GPIO.setup(8,  GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # CENTER
        

    def getInput(self, setButtons=False, delay=.1):
        status = []
        if setButtons: self.setGPIO()
        
        time.sleep(delay)
        status += ['up']     if GPIO.input(8)  == 0 else []
        status += ['select'] if GPIO.input(25) == 0 else []
        status += ['down']   if GPIO.input(7)  == 0 else []
        
        return status
    
        
    def displayMenu(self, options, returnOptions=False):
        self.setGPIO()
        self.drawMenu(options)
        sleepTimer = self.sleep
        
        while(True):
            time.sleep(.1)
            sleepTimer -= 1
            
            if GPIO.input(8) == 0:  # UP
                time.sleep(self.delay)
                options.insert(0, options.pop())
                self.drawMenu(options)
                sleepTimer=self.sleep
            
            if GPIO.input(25) == 0: # MID
                if isinstance(options[0], str): # [String]
                    return (options[0], options) if returnOptions else options[0]
                    
                elif (len(options[0])==2):      # [String, variable]
                    return (options[0][0], options) if returnOptions else options[0][0]
                

            if GPIO.input(7) == 0:  # DOWN
                time.sleep(self.delay)
                options.append(options.pop(0))
                self.drawMenu(options)
                sleepTimer=self.sleep

            if sleepTimer<=0:
                self.displayOff()
                while GPIO.input(7) and GPIO.input(8) and GPIO.input(25):
                    time.sleep(.1)
                sleepTimer=self.sleep


    def displayMessage(self, message):
        GPIO.setup(7,  GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
        GPIO.setup(8,  GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # CENTER
        
        (fontWidth, fontHeight) = self.font.getsize(message)
        start = 0 if fontWidth < self.display.width else self.display.width
        end   = 1 if fontWidth < self.display.width else -fontWidth
        step  = 1 if fontWidth < self.display.width else -self.scrollSpeed
        
        while True:
            for pos_x in range(start, end, step):
                self.draw.rectangle((0, 25, self.display.width, self.display.height - 25), outline=0, fill=1)
                self.draw.text((pos_x , 23), message, font = self.font, fill=0)
                self.display.image(self.image)
                self.display.show()

                while True:
                    if not GPIO.input(7) or not GPIO.input(8) or not GPIO.input(25):
                        self.draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0)
                        time.sleep(self.delay)
                        return
                    if end != 1:
                        time.sleep(.01)
                        break
                    time.sleep(.1)


    def displayLargeMessage(self, lines, color=0):
        GPIO.setup(7,  GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
        GPIO.setup(8,  GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # CENTER
        fromLine = 0 
        self.drawLargeMessage(lines[fromLine:fromLine+6], color)
        sleepTimer = self.sleep
        
        while(True):
            time.sleep(.1)
            sleepTimer -= 1
            
            if GPIO.input(8) == 0:  # UP
                time.sleep(self.delay)
                fromLine -= 1 if fromLine != 0 else 0
                self.drawLargeMessage(lines[fromLine:fromLine+6], color)
                sleepTimer=self.sleep
            
            if GPIO.input(25) == 0: # MID
                self.displayOff()
                return

            if GPIO.input(7) == 0:  # DOWN
                time.sleep(self.delay)
                fromLine += 1 if fromLine < len(lines)-6 else 0
                self.drawLargeMessage(lines[fromLine:fromLine+6], color)
                sleepTimer=self.sleep

            if sleepTimer<=0:
                self.displayOff()
                while GPIO.input(7) and GPIO.input(8) and GPIO.input(25):
                    time.sleep(.1)
                sleepTimer=self.sleep
        

    def displayToggle(self, label, options, position):
        GPIO.setup(7,  GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
        GPIO.setup(8,  GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # CENTER
        self.drawToggle(label, options, position)
        sleepTimer = self.sleep
        
        while(True):
            time.sleep(.1)
            sleepTimer -= 1
            
            if GPIO.input(8) == 0:  # UP
                time.sleep(self.delay)
                position = 0
                self.drawToggle(label, options, position)
                sleepTimer=self.sleep
            
            if GPIO.input(25) == 0: # MID
                time.sleep(self.delay)
                return(options[position])

            if GPIO.input(7) == 0:  # DOWN
                time.sleep(self.delay)
                position = 1
                self.drawToggle(label, options, position)
                sleepTimer=self.sleep

            if sleepTimer<=0:
                self.displayOff()
                while GPIO.input(7) and GPIO.input(8) and GPIO.input(25):
                    time.sleep(.1)
                sleepTimer=self.sleep
            

            
    def drawMenu(self, options):
        self.draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0) #Clear screen
        self.draw.rectangle((0, 26, self.display.width, 40), outline=0, fill=255)               #Draw selected marker
        for i in range(-2,3):
            if len(options) > abs(i):
                if isinstance(options[i], str): # [String]
                    self.draw.text((self.hshift[i] , self.vshift[i]), options[i], font=self.font, fill = 0 if i == 0 else 255) # Select Option
                elif (len(options[i])==2): # [String, variable]
                    self.draw.text((self.hshift[i] , self.vshift[i]), options[i][0], font=self.font, fill = 0 if i == 0 else 255) # Toggle Option
                    self.draw.ellipse((self.display.width - 11, self.vshift[i]+3, self.display.width - 1, self.vshift[i]+13), fill=255, width=1) # Toggle Option
                    self.draw.ellipse((self.display.width - 10, self.vshift[i]+4, self.display.width - 2, self.vshift[i]+13), fill=0, width=0) # Toggle Option
                    self.draw.ellipse((self.display.width - 9,  self.vshift[i]+5, self.display.width - 3, self.vshift[i]+12), fill=0 if options[i][1] == False else 255, width=0) # Toggle Option

        self.display.image(self.image)
        self.display.show()
        

    def drawToggle(self, label, options, position):
        self.draw.rectangle(( 10, 5, self.display.width-10, self.display.height-10) , outline=0, fill=255)
        self.draw.text((12 , 3), label, font=self.font, fill=0)
        self.draw.rectangle(( 20, 20, self.display.width-20, self.display.height-20) , outline=0, fill=0)

        if position == 0:
            self.draw.rectangle(( 21, 21, self.display.width/2, self.display.height-21) , outline=0, fill=255)
            self.draw.text((27 , 24),                    options[0], font=self.font, fill=0, anchor="ma")            
            #self.draw.text((self.display.width/2+8, 24), options[1], font=self.font, fill=1, anchor="rm")
        else:
            self.draw.rectangle(( self.display.width/2, 21, self.display.width-21, self.display.height-21) , outline=0, fill=255)
            #self.draw.text((27 , 24),                    options[0], font=self.font, fill=1, anchor="ma")            
            self.draw.text((self.display.width/2+8, 24), options[1], font=self.font, fill=0, anchor="rm")

        self.display.image(self.image)
        self.display.show()


    def drawLargeMessage(self, lines, color):
        y_pos = [-2,8,18,28,38,48]
        self.draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0 if color == 0 else 1)

        for i in range(0,len(lines)):
            self.draw.text((1, y_pos[i]), lines[i], font = self.font, fill= 1 if color == 0 else 0)
    
        self.display.image(self.image)
        self.display.show()
        
        
    def displayOff(self):
        self.draw.rectangle((0, 0, self.display.width, self.display.height), outline=0, fill=0)
        self.display.image(self.image)
        self.display.show()
        
