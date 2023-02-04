import time
import sys
import errno
import socket
import signal      # Required for handler
import pickle      # Required to convert objects to raw data
import select

from math import ceil as ceil
from threading import Thread, Event, Lock

sys.path.insert(1,'/opt/boobot/apps/Server/src/client')
from clientSocket import ClientSocket

PIXELS          = 16
DELAY           = .0167        # .0167 is about 60fps
CONFIRMATION    = True         # This helps prevent overloading the server
HEADERSIZE      = 10
IP              = ""          # socket.gethostname()
PORT            = 9000
TIMEOUT_SECONDS = 10
EXIT_SIG        = 1
BRIGHTNESS      = .2

# REQUIRED FOR THREADS
messageLock      = Lock()
newMessageEvent  = Event()
newMessageEvent.clear()


def handler(signum, frame):
    global EXIT_SIG
    
    if EXIT_SIG == 1: # Force shutdown
        exit()
    
    EXIT_SIG = 0
    print("Terminating program...", flush=True)
    

def getIP():
    global IP;
    if (IP == ""):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]

##################
# SERVER METHODS ########################################################################################################
##################
            
def sendToServer(message, pixelColors):
    with messageLock:
        message.clear()
        message += pixelColors[:]
        newMessageEvent.set()

        
def ClientManager(message):
    socket = ClientSocket(IP,PORT)
    
    while EXIT_SIG:
        newMessageEvent.wait()
        with messageLock:
            messageCopy = message[:]
            message.clear()
            newMessageEvent.clear()

        pixelData = [list(pixel) for pixel in messageCopy]
        jsonMessage = ('{"device":  "LED",'
                       '"command": "setPixels",'
                       '"colors":' + str(pixelData) +
                       '}')
        socket.send(jsonMessage)
        socket.recieve()        
        
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


def MapValue(value, fromMinimum, fromMaximum, toMinimum, toMaximum):
    if value==fromMaximum:
        return toMaximum #Rounding in the last line may cause it to return a greater value
    if value==fromMinimum:
        return toMinimum
    
    inMax    = abs(fromMinimum-fromMaximum)
    outMax   = abs(toMinimum-toMaximum)
    newValue = value - fromMinimum 

    return 0 if inMax==0 else (newValue*outMax/inMax)+toMinimum


def pixelBrightness(pixel, percentage):
    #Assuming the current color is max value
    dimmedColors =[]
    for maxColor in range(len(pixel)):
        dimmedColor = int(MapValue(percentage, 0, 100, 0, pixel[maxColor]))
        dimmedColors.append(dimmedColor)
            
    return tuple(dimmedColors)


def dimPixels(pixelColors, dim):
    for pixel in range(len(pixelColors)):
        dimmedColors = []
        
        for color in range(len(pixelColors[pixel])):
            dimmedColors.append(int(pixelColors[pixel][color]-dim if pixelColors[pixel][color]-dim>0 else 0))
            
        pixelColors[pixel] = tuple(dimmedColors)

    return pixelColors


def guage(value, pixelStep, colorSpeed, minValue, maxValue):
    pixelColors         = [(0,0,0)]*PIXELS
    lastColor           = [(0,0,0)]
    pixelsOn            = MapValue(value, minValue, maxValue, 0, PIXELS)
    lastPixelBrightness = (pixelsOn-int(pixelsOn))*100

    for pixel in range(ceil(pixelsOn)):
        pixelColors[pixel], pixelStep = rainbow(pixelStep)
        pixelStep   += colorSpeed

    if lastPixelBrightness != 0:
        pixelColors[ceil(pixelsOn)-1] = pixelBrightness(pixelColors[ceil(pixelsOn)-1], lastPixelBrightness)
            
    return pixelColors, pixelStep

    
def pixelCycle(message, step, colorSpeed, pixelPos, pixelSpeed, dim):
    pixelCount   = 16
    pixelStep    = step
    pixelColors  = [(0,0,0)]*pixelCount
    #pixelStep   = [(i*765/pixelCount) for i in range(pixelCount)]

    global EXIT_SIG
    
    while EXIT_SIG:
        
        time.sleep(DELAY)
        pixelStep += colorSpeed
        pixelPos  += pixelSpeed
        
        if pixelPos>=pixelCount:
            pixelPos = pixelPos%pixelCount;
        if pixelPos<0:
            pixelPos = pixelPos%pixelCount;
        
        pixelColors = dimPixels(pixelColors, dim)
        
        pixelColors[int(pixelPos)], pixelStep = rainbow(pixelStep)
        sendToServer(message, pixelColors)
            
def rainbowCycle(message, speed):
    pixelCount  = 16;
    pixelColors = [(0,0,0)]*pixelCount
    #pixelStep  = [0]*pixelCount
    pixelStep   = [(i*765/pixelCount) for i in range(pixelCount)]

    global EXIT_SIG
    
    while EXIT_SIG:
        time.sleep(DELAY)
        sendToServer(message, pixelColors)
        for i in range(pixelCount):
            pixelStep[i] += speed
            pixelColors[i], pixelStep[i] = rainbow(pixelStep[i])

def colorGlowCycle(message, pixelStep, speed, brightnessChange, brightness):
    pixelCount       = 16;
    pixelColors      = [(0,0,0)]

    global EXIT_SIG

    while EXIT_SIG:
        time.sleep(DELAY)
        sendToServer(message, pixelColors)
        
        brightness += brightnessChange;
        if not (0 <= brightness and brightness <= 100):
            brightnessChange = -brightnessChange
            brightness = 0 if brightness < 0 else 100

        pixelStep += speed
        pixelColors[0], pixelStep = rainbow(pixelStep)
        pixelColors[0] = pixelBrightness(pixelColors[0], brightness)

        
def pixelGuage(message, pixelStep, colorSpeed, subColorSpeed):
    pixelCount   = 16;

    global EXIT_SIG
    
    while EXIT_SIG:
        for value in range(301):
            pixelStep = checkStep(pixelStep)
            pixelColors, _ = guage(value, pixelStep, subColorSpeed, 0, 300)
            sendToServer(message, pixelColors)
            time.sleep(DELAY)

            pixelStep-=colorSpeed
            
            if not EXIT_SIG:
                return
            
        for value in range(300,-1,-1):
            pixelStep = checkStep(pixelStep)
            pixelColors, _ = guage(value, pixelStep, subColorSpeed, 0, 300)
            sendToServer(message, pixelColors)
            time.sleep(DELAY)

            pixelStep-=colorSpeed
            
            if not EXIT_SIG:
                return
        
def main():
    message    = []
    signal.signal(signal.SIGINT, handler)
    
    clientThread = Thread(target=ClientManager, args=(message, ))
    clientThread.start()
    
    #rainbowCycle(message, -3)          # socket, colorSpeed

    #colorGlowCycle(message, 255, 0,  .1,   3) # socket, stepStart, colorSpeed,  glowSpeed, brightness
    #colorGlowCycle(message,  0, 0,  0,   3) 
    #colorGlowCycle(message,  0, 0,  2, 100) 
    #colorGlowCycle(message,  0, 4,  2, 100) 

    #pixelCycle(message, 255, 0, 8,  0, 5)      # socket, stepStart, colorSpeed, pixelPos, pixelSpeed, dim
    #pixelCycle(message, 0, 1,  0, 1, 100)   
    #pixelCycle(message, 0, 4,  0, .2, 0)      
    #pixelCycle(message, 0, 0,  0, .2, 5)   
    #pixelCycle(message, 0, 1,  0,-.2, 5)   
    
    #pixelGuage(message, 0,  0, 0)      # stepStart, colorSpeed, subColorSpeed
    #pixelGuage(message, 0,  0, 17.4)   
    #pixelGuage(message, 0,  2,  0)     
    #pixelGuage(message, 5, 10, -50)     
    
    pixelColors = [(0,0,0)]*PIXELS
    sendToServer(message, pixelColors)
    
if __name__ == "__main__":
    main()
