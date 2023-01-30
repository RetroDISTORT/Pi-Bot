#cc -fPIC -Wall -Wextra -O2 `pkg-config --cflags libpulse-simple` -shared -pthread -lm `pkg-config --libs libpulse-simple` -o vu.so vu.c
import time

import errno       # Required for sockets
import socket      # Required for sockets
import signal      # Required for handler
import pickle      # Required to convert objects to raw data
import select      # Required for sockets

import ctypes
import board
import board            # Required for I2C bus
import busio            # Required for I2C bus
import digitalio        # Required for I2C bus
import adafruit_ina219  # Required for voltage sensor
import adafruit_ssd1306 # Required for OLED displays

import numpy    as np
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

from math import ceil as ceil
from PIL  import Image, ImageDraw, ImageFont

EXIT_SIG = 1

# REQUIRED FOR SOUND CAPTURE 
server    = ""
device    = "0"
channels  = 2           #    0 <  channels < 32
rate      = 48000       #  128 <   rate    < 250000
updates   = 60          #    1 <  updates  < 200
peak      = "" 
samples   = ctypes.c_size_t(int(rate/updates))
delayTime = 1/updates * (1/updates*.1)

# REQUIRED FOR RGB LEDS
PIXELS          = 16
DELAY           = 1/updates    # .0167 is about 60fps
CONFIRMATION    = True         # This helps prevent overloading the server
HEADERSIZE      = 10
IP              = ""  # socket.gethostname()
PORT            = 1235
TIMEOUT_SECONDS = 10


def handler(signum, frame):
    global EXIT_SIG
    EXIT_SIG = 0
    print("Terminating program...", flush=True)


def getIP():
    global IP;
    if (IP == ""):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]

        
def GetFonts(dir):
    fontXXL = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 32)
    fontXL  = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 18)
    fontL   = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 16)
    fontM   = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 12)
    fontS   = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 10)
    fontXS  = ImageFont.truetype(dir+"ratchet-clank-psp.ttf",  8)
    fontXXS = ImageFont.truetype(dir+"3x3-Mono.ttf",  4)
    
    return [fontXXL, fontXL, fontL, fontM, fontS, fontXS, fontXXS]

##################
# SERVER METHODS ########################################################################################################
##################

def createClientSocket(IP, PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    
    return client_socket


def sendMessage(socket, obj):    
    msg = pickle.dumps(obj)
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+msg
    #print(msg)
    socket.send(msg)

    
def ConfirmationResponse(socket):
    if CONFIRMATION == False:
        return
    
    msg = recieveMessage(socket)
    if msg==False:
        print("Bad Server Response\n Closing Program.")
        exit()

    
def recieveMessage(socket):
    while EXIT_SIG:
        try:
            full_msg = b''
        
            while True:
                msg = socket.recv(16)
            
                if len(full_msg)==0:
                    msglen = int(msg[:HEADERSIZE])
                    new_msg = False

                full_msg += msg

                if len(full_msg)-HEADERSIZE == msglen:
                    return full_msg[HEADERSIZE:]

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

                # We just did not receive anything
                continue

        except Exception as e:
            print('Reading error: '.format(str(e)))
            exit()
            
###########################
# RGB PIXEL COLOR CONTROL ###############################################################################################
###########################

def checkStep(step):
    if step > 765:             # RESET TO A STATE IN RANGE
        step = step - 765
    if 0 > step:
        step = 765 + step
        
    return step

def rainbow(step):
    step = checkStep(step)
    
    if step<255:               # From 0 - 255
        R=255-step
        G=step
        B=0
    else:
        if step<510:           # From 255 - 510
            R=0
            G=510-step
            B=step-255
        else:                  # From 510 - 765
            R=step-510
            G=0
            B=765-step      
            
    return (int(R),int(G),int(B)), step


def pixelBrightness(pixel, percentage):
    #Assuming the current color is max value
    dimmedColors =[]
    for maxColor in range(len(pixel)):
        dimmedColor = int(MapValue(percentage, 0, 100, 0, pixel[maxColor]))
        dimmedColors.append(dimmedColor)
            
    return tuple(dimmedColors)


def guage(value, pixelStep, colorSpeed, minValue, maxValue):
    pixelColors         = [(0,0,0)]*PIXELS
    lastColor           = [(0,0,0)]
    pixelsOn            = MapValue(value, minValue, maxValue, 0, PIXELS)
    lastPixelBrightness = (pixelsOn-int(pixelsOn))*100

    #print(str(pixelsOn)+" "+str(value)+" "+str(maxValue))
    
    for pixel in range(ceil(pixelsOn)):
        pixelColors[pixel], pixelStep = rainbow(pixelStep)
        pixelStep   += colorSpeed

    if lastPixelBrightness != 0:
        pixelColors[ceil(pixelsOn)-1] = pixelBrightness(pixelColors[ceil(pixelsOn)-1], lastPixelBrightness)

            
    return pixelColors, pixelStep

####################
# VU METER METHODS ######################################################################################################
####################

def CreateVU(vulib):
    if vulib.vu_start(server, "vu-bar", device, "VU monitor", channels, rate, samples):
        print(f'Cannot monitor audio source')
        exit()

        
def ReadFromVU(vulib):
    new_peak = (ctypes.c_float * channels)()
    while vulib.vu_peak(new_peak, channels) != channels:
        time.sleep(delayTime)
        
    return(new_peak)
                

def EndVU(vulib):
    vulib.vu_stop()

###############
# OTHER TOOLS ###########################################################################################################
###############

def MapValue(value, fromMinimum, fromMaximum, toMinimum, toMaximum):
    inMax    = abs(fromMinimum-fromMaximum)
    outMax   = abs(toMinimum-toMaximum)
    newValue = value - fromMinimum 

    return 0 if inMax==0 else (newValue*outMax/inMax)+toMinimum


def GraphArray(draw, array):
    maxGraph = max(array)
    minGraph = min(array) if maxGraph != 0 else -1 # Prevent division by 0 when mapping values

    for i in range(len(array)-1):
        value1 = 52 - MapValue(array[i]  , minGraph, maxGraph, 0, 52)
        value2 = 52 - MapValue(array[i+1], minGraph, maxGraph, 0, 52)

        draw.line( ((i), value1, (i+1), value2), width=0, fill=255) # Voltage Line

    return maxGraph, minGraph


def VUPrint(vulib):
    while EXIT_SIG:
        peaks = ReadFromVU(vulib)
        for c in range(channels):
            print("%.15f" % peaks[c], end = "\n" if c==channels-1 else " ")

            
def VUBars(vulib, decay, reset):
    i2c     = busio.I2C(board.SCL, board.SDA)
    display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    image   = Image.new('1', (display.width, display.height))
    draw    = ImageDraw.Draw(image)

    display.contrast(1)
    
    maxVU  = 0
    count  = 0
    CPeaks = [0]*2
    CNames = ["L", "R"]
    fonts  = GetFonts('/opt/boobot/fonts/')
    
    while EXIT_SIG:

        if count == 0:
            count = reset
            maxVU = 0
        else:
            count-=1
        
        newPeaks = ReadFromVU(vulib)
        
        if max(newPeaks)>maxVU:
                maxVU = max(newPeaks)
                CPeaks = [0]*2
                
        for c in range(min(channels,2)):
            CPeaks[c] *= decay
            CPeaks[c]  = newPeaks[c] if newPeaks[c] > CPeaks[c] else CPeaks[c]
            height = 60-MapValue(CPeaks[c], 0, maxVU, 0, 55)
            draw.rectangle((-1+c*15, 55, 15+c*15, height), outline=0, fill=255)
            draw.text((4+c*15, 53), CNames[c], font=fonts[3], anchor='mm', fill=255)
        
        draw.text((40, 10), "Device:   " + str(device), font=fonts[3], anchor='mm', fill=255)
        draw.text((40, 20), "Channels: " + str(channels), font=fonts[3], anchor='mm', fill=255)
        draw.text((40, 30), "Rate: " + str(rate), font=fonts[3], anchor='mm', fill=255)
        draw.text((40, 40), "Samples: " + str(int(rate/updates)), font=fonts[3], anchor='mm', fill=255)
        draw.text((40, 50), "Updates: " + str(updates), font=fonts[3], anchor='mm', fill=255)
        
        display.image(image)
        display.show()
        draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)

        
def VUGraph(vulib):
    i2c     = busio.I2C(board.SCL, board.SDA)
    display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    image   = Image.new('1', (display.width, display.height))
    draw    = ImageDraw.Draw(image)

    display.contrast(1)
    
    valHist = [0] * 50
    while EXIT_SIG:
        peaks = ReadFromVU(vulib)
        valHist.append(peaks[0])
        valHist.pop(0)
        draw.rectangle((0, 0, display.width, display.height), outline=0, fill=0)
        GraphArray(draw, valHist)
        display.image(image)
        display.show()
        
    display.fill(0)
    display.show()

        
def VURGB(vulib, pixelStep, colorSpeed, subColorSpeed, decay, reset):
    getIP()
    socket      = createClientSocket(IP, PORT)
    pixelCount  = 16;
    maxVU       = 0
    count       = 0
    CPeaks      = [0]*2

    
    while EXIT_SIG:
        if count == 0:
            count = reset
            maxVU = 0
        else:
            count-=1
        
        newPeaks = ReadFromVU(vulib)
        
        if newPeaks[0]>maxVU:
            maxVU  = newPeaks[0]
            CPeaks = [0]*2

        CPeaks[0] *= decay
        CPeaks[0]  = newPeaks[0] if newPeaks[0] > CPeaks[0] else CPeaks[0]
        volume     = MapValue(CPeaks[0], 0, maxVU, 0, 5000)
            
        pixelStep = checkStep(pixelStep)
        pixelColors, _ = guage(volume, pixelStep, subColorSpeed, 0, 5000)
        sendMessage(socket, pixelColors)
        ConfirmationResponse(socket)
        time.sleep(DELAY)

        pixelStep-=colorSpeed
        
    pixelColors = [(0,0,0)]*PIXELS
    sendMessage(socket, pixelColors)
    ConfirmationResponse(socket)        
    
def main():
    vulib   = ctypes.CDLL('./vu.so')
    CreateVU(vulib)

    #VUPrint(vulib)
    #VUBars(vulib, .1, 40)
    #VUGraph(vulib)
    VURGB(vulib, 0, -2, 17.4, .95, 4000)
    
    EndVU(vulib)
    
if __name__ == "__main__":
    main()
