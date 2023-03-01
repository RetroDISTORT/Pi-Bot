import time
import sys
import errno
import socket
import signal      # Required for handler
import select

from math import ceil as ceil
from threading import Thread, Event, Lock

sys.path.insert(1,'/opt/boobot/apps/Server/src/client')
from clientSocket import ClientSocket

PIXELS          = 16
HEADERSIZE      = 10
IP              = ""
PORT            = 9001
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
    getIP()
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
    
            
def colorGlowCycle(message, pixelStep, speed, brightnessChange, brightness):
    pixelCount       = 16;
    pixelColors      = [(0,0,0)]

    global EXIT_SIG

    while EXIT_SIG:
        time.sleep(.01)
        sendToServer(message, pixelColors)
        
        brightness += brightnessChange;
        if not (0 <= brightness and brightness <= 100):
            brightnessChange = -brightnessChange
            brightness = 0 if brightness < 0 else 100

        pixelStep += speed
        pixelColors[0], pixelStep = rainbow(pixelStep)
        pixelColors[0] = pixelBrightness(pixelColors[0], brightness)

        
def main(stepStart, colorSpeed, glowSpeed, brightness):
    message    = []
    signal.signal(signal.SIGINT, handler)
    
    clientThread = Thread(target=ClientManager, args=(message, ))
    clientThread.start()
    
    colorGlowCycle(message, stepStart, colorSpeed, glowSpeed, brightness) # socket, stepStart, colorSpeed,  glowSpeed, brightness
    
    pixelColors = [(0,0,0)]*PIXELS
    sendToServer(message, pixelColors)
    
    
if __name__ == "__main__":
    #if len(sys.argv) != 2 or not sys.argv[1].isnumeric():
    #    print("Usage: python3 rainbowCycle.py [COLORSPEED]", sys.argv[1])
    #    exit()
    
    main(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]))
