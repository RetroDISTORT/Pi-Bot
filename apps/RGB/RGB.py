import time
import errno
import socket
import signal      # Required for handler
import pickle      # Required to convert objects to raw data
import select
from math import ceil as ceil

PIXELS          = 16
DELAY           = .0167        # .0167 is about 60fps
CONFIRMATION    = True         # This helps prevent overloading the server
HEADERSIZE      = 10
IP              = ""           # socket.gethostname()
PORT            = 1235
TIMEOUT_SECONDS = 10
EXIT_SIG        = 1
BRIGHTNESS      = .2

def handler(signum, frame):
    global EXIT_SIG
    EXIT_SIG = 0
    
    print("Sending end signal to server...", flush=True)

def getIP():
    global IP;
    if (IP == ""):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]

        
def sendSetup(socket):
    sendMessage(socket, ["Confirmation", CONFIRMATION])
    ConfirmationResponse(socket)
    sendMessage(socket, ["Brightness", BRIGHTNESS])
    ConfirmationResponse(socket)
    
    
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

def mapValue(value, fromMinimum, fromMaximum, toMinimum, toMaximum):
    #
    # USAGE EXAMPLE 
    #
    # for i in range(101):
    #     print(str(i) + "\t-\t" + str(mapValue(i, 0, 100, 0, 255)))
    inMax    = abs(fromMinimum-fromMaximum)
    outMax   = abs(toMinimum-toMaximum)
    newValue = value - fromMinimum 

    return 0 if outMax<=0 else (newValue*outMax/inMax)+toMinimum

def pixelBrightness(pixel, percentage):
    #Assuming the current color is max value
    dimmedColors =[]
    for maxColor in range(len(pixel)):
        dimmedColor = int(mapValue(percentage, 0, 100, 0, pixel[maxColor]))
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
    pixelsOn            = mapValue(value, minValue, maxValue, 0, PIXELS)
    lastPixelBrightness = (pixelsOn-int(pixelsOn))*100

    for pixel in range(ceil(pixelsOn)):
        pixelColors[pixel], pixelStep = rainbow(pixelStep)
        pixelStep   += colorSpeed

    if lastPixelBrightness != 0:
        pixelColors[ceil(pixelsOn)-1] = pixelBrightness(pixelColors[ceil(pixelsOn)-1], lastPixelBrightness)

            
    return pixelColors, pixelStep

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
                _, _, _ = select.select([socket], [], []) #Waits for a socket signal
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
    
def pixelCycle(socket, step, colorSpeed, pixelPos, pixelSpeed, dim):
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
        sendMessage(socket, pixelColors)
        ConfirmationResponse(socket)
            
def rainbowCycle(socket, speed):
    pixelCount  = 16;
    pixelColors = [(0,0,0)]*pixelCount
    #pixelStep  = [0]*pixelCount
    pixelStep   = [(i*765/pixelCount) for i in range(pixelCount)]

    global EXIT_SIG
    
    while EXIT_SIG:
        time.sleep(DELAY)
        sendMessage(socket, pixelColors)
        ConfirmationResponse(socket)
        for i in range(pixelCount):
            pixelStep[i] += speed
            pixelColors[i], pixelStep[i] = rainbow(pixelStep[i])

def colorGlowCycle(socket, pixelStep, speed, brightnessChange, brightness):
    pixelCount       = 16;
    pixelColors      = [(0,0,0)]

    global EXIT_SIG

    while EXIT_SIG:
        time.sleep(DELAY)
        sendMessage(socket, pixelColors*pixelCount)
        ConfirmationResponse(socket)
        
        brightness += brightnessChange;
        if not (0 <= brightness and brightness <= 100):
            brightnessChange = -brightnessChange
            brightness = 0 if brightness < 0 else 100

        pixelStep += speed
        pixelColors[0], pixelStep = rainbow(pixelStep)
        pixelColors[0] = pixelBrightness(pixelColors[0], brightness)

        
def pixelGuage(socket, pixelStep, colorSpeed, subColorSpeed):
    pixelCount   = 16;

    global EXIT_SIG
    
    while EXIT_SIG:
        for value in range(301):
            pixelStep = checkStep(pixelStep)
            pixelColors, _ = guage(value, pixelStep, subColorSpeed, 0, 300)
            sendMessage(socket, pixelColors)
            ConfirmationResponse(socket)
            time.sleep(DELAY)

            pixelStep-=colorSpeed
            
            if not EXIT_SIG:
                return
            
        for value in range(300,-1,-1):
            pixelStep = checkStep(pixelStep)
            pixelColors, _ = guage(value, pixelStep, subColorSpeed, 0, 300)
            sendMessage(socket, pixelColors)
            ConfirmationResponse(socket)
            time.sleep(DELAY)

            pixelStep-=colorSpeed
            
            if not EXIT_SIG:
                return
        
def main():

    signal.signal(signal.SIGINT, handler)
    getIP()
    client_socket  = createClientSocket(IP, PORT)
    
    sendSetup(client_socket)
    
    #rainbowCycle(client_socket, -3)          # socket, colorSpeed

    #colorGlowCycle(client_socket, 255, 0,  .1,   3) # socket, stepStart, colorSpeed,  glowSpeed, brightness
    #colorGlowCycle(client_socket,   0, 0,  0,   3) 
    #colorGlowCycle(client_socket,   0, 0,  2, 100) 
    #colorGlowCycle(client_socket,   0, 4,  2, 100) 

    #pixelCycle(client_socket, 255, 0, 8,  0, 5)      # socket, stepStart, colorSpeed, pixelPos, pixelSpeed, dim
    pixelCycle(client_socket, 0, 1,  0, 1, 100)   
    #pixelCycle(client_socket, 0, 4,  0, .2, 0)      
    #pixelCycle(client_socket, 0, 0,  0, .2, 5)   
    #pixelCycle(client_socket, 0, 1,  0,-.2, 5)   
    
    #pixelGuage(client_socket, 0,  0, 0)      # stepStart, colorSpeed, subColorSpeed
    #pixelGuage(client_socket, 0,  0, 17.4)   
    #pixelGuage(client_socket, 0,  2,  0)     
    #pixelGuage(client_socket, 5, 10, -50)     
    
    pixelColors = [(0,0,0)]*PIXELS
    sendMessage(client_socket, pixelColors)
    ConfirmationResponse(client_socket)
    
if __name__ == "__main__":
    main()
