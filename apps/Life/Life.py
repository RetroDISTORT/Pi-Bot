import time
import board
import busio
import random
import digitalio
import adafruit_ssd1306

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

from PIL import Image, ImageDraw, ImageFont

def get_fonts(dir):
    fontXXL = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 32)
    fontXL  = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 18)
    fontL   = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 16)
    fontM   = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 12)
    fontS   = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 10)
    fontXS  = ImageFont.truetype(dir+"ratchet-clank-psp.ttf",  8)
    fontXXS = ImageFont.truetype(dir+"3x3-Mono.ttf",  4)
    
    return [fontXXL, fontXL, fontL, fontM, fontS, fontXS, fontXXS]

#def loadWorld():


#def saveWorld():

def cellFunction(state, neighbors, survive, spawn):
    if state == 1:
        return 1 if neighbors in survive else 0
    
    if state == 0:
        return 1 if neighbors in spawn else 0
        
    return 0

def newDay(world, survive, spawn):
    height   = len(world)
    width    = len(world[0])
    newWorld = createEmptyWorld(width,height)
    
    for y in range(height):
        for x in range(width):
            newStatus = cellFunction(world[y][x], neighbors(x,y,world), survive, spawn)
            newWorld[y].pop(x)
            newWorld[y].insert(x, newStatus)
    
    clone(newWorld, world)

def clone(from_world, to_world):
    height   = len(from_world)
    width    = len(from_world[0])
    
    for y in range(height):
        for x in range(width):
            to_world[y].pop(0)
            to_world[y].insert(width,from_world[y][x])
    
def neighbors(x,y,world):
    height = len(world)
    width  = len(world[0])
    count  = 0
    debug  = 0

    for check_y in range(y-1,y+2):
        for check_x in range(x-1,x+2):
            if not (check_x == x and check_y == y):                
                count += 1 if world[check_y if check_y < height else 0][check_x if check_x < width else 0] == 1 else 0
                
    return count

def createEmptyWorld(width, height):
    return [[0] * width for i in range(height)]

def createRandomWorld(width, height, seed=random, population=50):
    random.seed(seed)
    return [[1 if random.randint(0,100) < population else 0  for i in range(width)] for j in range(height)]

def startGame(screen, ruleSurvive, ruleSpawn, seed):
    world = createRandomWorld(10, 64, seed = 5, population = 99)
    
    while(True):
        drawWorld(screen, world)
        newDay(world, ruleSurvive, ruleSpawn)
        
def drawWorld(screen, world):
    width  = len(world[0])
    height = len(world)
    
    image = Image.new('1', (screen.width, screen.height))
    draw = ImageDraw.Draw(image)

    #DrawScreen
    for y in range(height):
        #print(world[y])
        for x in range(width):
            if world[y][x] == 1:
                draw.point((x,y), 255)
                      
    screen.image(image)
    screen.show()


def menu(screen, fonts):
    image = Image.new('1', (screen.width, screen.height))
    draw = ImageDraw.Draw(image)

    ruleSurvive = [2,3,7,8,9]
    ruleSpawn   = [3,8]
    seed = "random";

    #SideBar
    draw.rectangle((0, 0, 60, screen.height), outline=0, fill=255)
    draw.text((15,  0), "LIFE"   , font=fonts[1], anchor='mm', fill = 0)
    draw.text((10, 20), "Survive", font=fonts[3], anchor='lm', fill = 0)
    draw.text((10, 29), "Spawn"  , font=fonts[3], anchor='lm', fill = 0)
    draw.text((10, 40), "Seed"   , font=fonts[3], anchor='lm', fill = 0)
    draw.text((10, 50), "Start"  , font=fonts[3], anchor='lm', fill = 0)
    draw.ellipse((3, 25, 7, 29), fill=0)
    
    #draw.text((63, 10), "123456789"  , font=fonts[3], anchor='mm', fill = 255)
    vals = ''.join(str(i) for i in ruleSurvive)
    draw.text((63, 22), vals, font=fonts[3], anchor='lm', fill = 255)
    vals = ''.join(str(i) for i in ruleSpawn)
    draw.text((63, 33), vals, font=fonts[3], anchor='lm', fill = 255)
    draw.text((63, 42), seed, font=fonts[3], anchor='lm', fill = 255)
    
    
    screen.image(image)
    screen.show()
    
    startGame(screen, ruleSurvive, ruleSpawn, seed)

def main():
    WIDTH = 128
    HEIGHT = 64
    BORDER = 0
    
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    fontList = get_fonts('/opt/boobot/fonts/')

    oled.contrast(1) # Max contrast is 255
    
    GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
    GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) # CENTER
    
    #oled.fill(0)
    #oled.show()


    time.sleep(1)
    
    done = False

    
    #while(not done):
    #    done = done or GPIO.input(7)  == 0 # DOWN
    #    done = done or GPIO.input(8)  == 0 # UP
    #    done = done or GPIO.input(25) == 0 # CENTER
    menu(oled, fontList)

    time.sleep(.1)
        
if __name__ == "__main__":
    main()
