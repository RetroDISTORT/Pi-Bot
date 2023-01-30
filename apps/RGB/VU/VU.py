import time

import errno       # Required for sockets
import socket      # Required for sockets
import signal      # Required for handler
import pickle      # Required to convert objects to raw data
import select      # Required for sockets
import pasimple
import numpy as np

from math import ceil as ceil
from struct import unpack
from threading import Thread, Event, Lock

EXIT_SIG = 1                           # Tells all threads to end

# REQUIRED FOR SOUND CAPTURE 
audio_server    = ""
audio_device    = "0" 
audio_channels  = 2                    #    0 <  channels < 32
audio_rate      = 48000                #  128 <   rate    < 250000
audio_updates   = 30                   #    1 <  updates  < 200
audio_samples   = int(audio_rate/audio_updates)*2#2048                 # ctypes.c_size_t(int(rate/updates))
audio_direction = pasimple.PA_STREAM_RECORD
audio_format    = pasimple.PA_SAMPLE_S16LE
audio_app_name  = 'pythonVU'
audio_stream    = None
audio_server    = None

# REQUIRED FOR RGB LEDS
PIXELS          = 16
DELAY           = 1/audio_updates      # .0167 is about 60fps
HEADERSIZE      = 10
IP              = "10.0.0.17"          # socket.gethostname()
PORT            = 1235
CONFIRMATION    = True                 # This helps prevent overloading the server
BRIGHTNESS      = .1

# REQUIRED FOR THREADS
messageLock      = Lock()
newMessageEvent  = Event()
newMessageEvent.clear()

# REQUIRED FOR SERVER OPTIONS
SERVERMODE       = True



def handler(signum, frame):
    global EXIT_SIG
    
    if EXIT_SIG == 1: # Force shutdown
        exit()
    
    EXIT_SIG = 0
    print("Terminating program...", flush=True)


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
    socket.send(msg)

    
def ConfirmationResponse(socket):
    global EXIT_SIG
    
    if CONFIRMATION == False:
        return

    msg = recieveMessage(socket)
    if msg==False:
        print("Bad Server Response\n Closing Program.")
        EXIT_SIG = 0
        exit()

        
def recieveMessage(socket):
    global EXIT_SIG
    
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
                EXIT_SIG = 0
                exit()

            # We just did not receive anything
            continue

        except Exception as e:
            print('Reading error: '.format(str(e)))
            EXIT_SIG = 0
            exit()

            
def sendToServer(socket, message, pixelColors):
    if SERVERMODE:                    # Send a thread to handle messages
        with messageLock:
            message.clear()
            message += pixelColors[:]
            newMessageEvent.set()         
    else:                             # Send without using thread
        sendMessage(socket, pixelColors)
        ConfirmationResponse(socket)

        
###########################
# RGB PIXEL COLOR CONTROL ###############################################################################################
###########################

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


def guage(value, pixels, pixelStep, colorSpeed, minValue, maxValue):
    pixelColors         = [(0,0,0)]*pixels
    lastColor           = [(0,0,0)]
    pixelsOn            = MapValue(value, minValue, maxValue, 0, pixels)
    lastPixelBrightness = (pixelsOn-int(pixelsOn))*100
    
    for pixel in range(ceil(pixelsOn)):
        pixelColors[pixel], pixelStep = rainbow(pixelStep)
        pixelStep   += colorSpeed

    if lastPixelBrightness != 0:
        pixelColors[ceil(pixelsOn)-1] = pixelBrightness(pixelColors[ceil(pixelsOn)-1], lastPixelBrightness)

            
    return pixelColors, pixelStep

def brightnessGuage(value, pixels, minValue, maxValue):
    brightness          = [0]*pixels
    pixelsOn            = MapValue(value, minValue, maxValue, 0, pixels)
    lastPixelBrightness = (pixelsOn-int(pixelsOn))*100

    for pixel in range(ceil(pixelsOn)):
        brightness[pixel] = 100

    if lastPixelBrightness != 0:
        brightness[ceil(pixelsOn)-1] = lastPixelBrightness

    return brightness

####################
# VU METER METHODS ######################################################################################################
####################

def CreateVU():
    return pasimple.PaSimple(audio_direction, audio_format, audio_channels, audio_rate, app_name=audio_app_name, stream_name=audio_stream, server_name=audio_server, device_name=audio_device)


def EndVU(audio):
    audio.close()

###############
# OTHER TOOLS ###########################################################################################################
###############

def MapValue(value, fromMinimum, fromMaximum, toMinimum, toMaximum):
    if value==fromMaximum:
        return toMaximum #Rounding in the last line may cause it to return a greater value
    if value==fromMinimum:
        return toMinimum
    
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


def power_index(val):
    return int(2 * int(audio_samples) * val / audio_rate)


def fft_3point(data):
    matrix    = [0, 0, 0]
    weighting = [    1,   8,   16]
    ranges    = [0, 200, 1000, 8000]

    fourier = np.fft.rfft(data)
    fourier = np.delete(fourier, len(fourier) - 1)

    #print(len(fourier))
    power = np.abs(fourier)
    for i in range(len(ranges)-1):
        matrix[i] = int(np.mean(power[power_index(ranges[i]) : power_index(ranges[i+1]) :1]))
    
    #matrix = np.divide(np.multiply(matrix, weighting), 100000)
    #matrix = matrix.clip(1)
    matrix = [float(m) for m in matrix]
    return matrix
    

def compute_fft(data):
    power     = []
    bins      = 16
    matrix    = [0]*bins
    weighting = [1,  1, 2, 2, 4, 4, 4, 8, 8, 8, 8, 16, 16, 16, 16, 16]

    # 4096@48000
    ranges =    [0, 300, 500, 700, 800, 1000, 1200, 1400, 1500, 1800, 2000, 3000, 4000, 5000, 6000, 7000, 8000]
    # 1024@48000
    #ranges =    [0, 40, 80, 125, 200, 400, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 7000, 8000]
    # 512
    #ranges =    [0, 100, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 7000, 7500]
    # 256
    #ranges =    [0, 100, 200, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000, 4000, 5000, 6000, 7000, 7500]
    # 128
    #ranges =    [0, 350, 520, 700, 900, 1050, 1300, 1400, 1500, 1700, 1900, 2100, 2300, 2500, 2700, 2900, 3500]
    # 128@16000Hz
    #ranges =    [0, 350, 520, 700, 900, 1050, 1300, 1400, 1500, 1700, 1900, 2100, 2300, 2400, 2500, 2600, 2700]
    # 128@1000Hz
    #ranges =    [0, 500, 1000, 2000, 900, 1050, 1300, 1400, 1500, 1700, 1900, 2100, 2300, 2400, 2500, 2600, 2700]
    
    fourier = np.fft.rfft(data)
    fourier = np.delete(fourier, len(fourier) - 1)

    #print(len(fourier))
    power = np.abs(fourier)
    for i in range(len(ranges)-1):
        #print(ranges[i], end = ":")
        #print(power_index(ranges[i]))
        matrix[i] = int(np.mean(power[power_index(ranges[i]) : power_index(ranges[i+1]) :1]))
    
    
    matrix = np.divide(np.multiply(matrix, weighting), 100000)#10000000000)
    #matrix = matrix.clip(1)
    matrix = [float(m) for m in matrix]
    return matrix


def VUSampleLE():
    audio = CreateVU()
    while EXIT_SIG:
        left_channel_data  = []
        right_channel_data = []
        audio_data = audio.read(audio_channels * audio_samples * pasimple.format2width(audio_format))

        data = unpack("%dh" % (len(audio_data)/2), audio_data)
        data = np.array(data, dtype='h')

        print("Left Channel:")
        print(data[0::2]) #Read only the first channel
        print("Right Channel:")
        print(data[1::2]) #Read only the second channel
            
    EndVU(audio)

    
def VUFFT():
    audio = CreateVU()
    while EXIT_SIG:
        audio_data = audio.read(audio_channels * audio_samples * pasimple.format2width(audio_format))
        data = unpack("%dh" % (len(audio_data) / 2), audio_data)
        data = np.array(data, dtype='h')
        leftChannel = data[0::2]
        bins = compute_fft(leftChannel)
        print(bins)
        
    EndVU(audio)


def VUDFTRGB(message):
    audio       = CreateVU()
    socket      = createClientSocket(IP, PORT)
    decay       = .9
    pixelCount  = 16
    count       = 0
    bins        = pixelCount
    pixelStep   = 0
    stepSpeed   = 50
    color       = 0
    colorSpeed  = 10 
    brightness  = [0]*16
    extra       = 1      #Prevents dead time
    resetMax    = 40000  # How often is max gets reset
    resetCount  = 0
    VUMax       = 0
    boost       = 2
    
    while EXIT_SIG:
        audio_data = audio.read(audio_channels * audio_samples * pasimple.format2width(audio_format)*extra)
        audio_data = audio_data[:int(len(audio_data)/extra)]
        data = unpack("%dh" % (len(audio_data) / 2), audio_data)
        data = np.array(data, dtype='h')
        leftChannel = data[0::2]
        
        pixelColors = [(0,0,0)]*PIXELS
        VULevels = compute_fft(leftChannel)

        if resetCount > resetMax:
            resetCount = 0
            VUMax = 0
            
        VUMax = VUMax if VUMax > max(VULevels) else max(VULevels)

        color += colorSpeed
        color = checkStep(color)
        pixelStep = color
        for i in range(16):
            brightness[i] *= decay
            brightness[i]  = VULevels[i] if VULevels[i] > brightness[i] else brightness[i]
            VULevels[i] = VUMax if VULevels[i]*boost >= VUMax else VULevels[i]*boost #have more leds reach max

            pixelStep   += stepSpeed
            pixelColors[i], _ = rainbow(pixelStep) # Rainbow color

            #pixelColors[i], pixelStep = rainbow(int(MapValue(VULevels[i], 0, VUMax, 0, 255))) # Intensity

            pixelColors[i] = pixelBrightness(pixelColors[i], MapValue(brightness[i], 0, VUMax, 0, 100))

        sendToServer(socket, message, pixelColors)

            

def VUDFTRGB3P(message):
    audio         = CreateVU()
    socket        = createClientSocket(IP, PORT)
    decay         = .80
    pixelCount    = 16
    color         = 0
    subColor      = 0
    colorSpeed    = 4
    subColorSpeed = 50
    extra         = 1      #Prevents dead time due to slow buffer extraction

    value       = [0,0,0]
    levelPixels = [5,6,5]
    maxValue    = [5,5,5]

    while EXIT_SIG:

        audio_data = audio.read(audio_channels * audio_samples * pasimple.format2width(audio_format)*extra)
        audio_data = audio_data[:int(len(audio_data)/extra)]
        data = unpack("%dh" % (len(audio_data) / 2), audio_data)
        data = np.array(data, dtype='h')
        leftChannel = data[0::2]
        
        newValues = fft_3point(leftChannel)
        
        
        pixelColors = [(0,0,0)]*PIXELS
        brightness  = [[0],[0],[0]]
        #Update max values
        for i in range(3):
            maxValue[i] = newValues[i] if newValues[i] > maxValue[i] else maxValue[i]
        
        for i in range(3):
            value[i]         *= decay
            value[i]          = newValues[i] if newValues[i] > value[i] else value[i]
            #value       = maxValue
            brightness[i]     = brightnessGuage(value[i], ceil(levelPixels[i]/2), -1, maxValue[i])
            if levelPixels[i]%2 == 0:
                brightness[i]     = brightness[i][::-1]
                brightness[i]    += brightness[i][::-1]
            else:
                brightness[i]     = brightness[i][::-1]
                brightness[i]    += brightness[i][1::-1]

        allBrightness = []
        
        for b in brightness:
            allBrightness += b

        for i in allBrightness:
            if i > 100 or i < 0:
                print(i)

        if len(allBrightness) > 16:
            print("error!")
            
        color += colorSpeed
        color = checkStep(color)
        pixelStep = color
        for pixel in range(pixelCount):
            pixelStep                    += subColorSpeed
            pixelColors[pixel], pixelStep = rainbow(pixelStep)
            pixelColors[pixel]            = pixelBrightness(pixelColors[pixel], max(allBrightness[pixel],2))

        sendToServer(socket, message, pixelColors)
    
    
def RGB_OFF():
    socket      = createClientSocket(IP, PORT)
    pixelCount  = 16;
        
    pixelColors = [(0,0,0)]*PIXELS
    sendToServer(socket, message, pixelColors)


def VURGB(message, pixelStep, colorSpeed, subColorSpeed, decay, reset):
    socket      = createClientSocket(IP, PORT)
    audio       = CreateVU()
    pixelCount  = 16;
    maxVU       = 0
    count       = 0
    CPeaks      = [0]*2

    #sendSetup(socket)
    
    while EXIT_SIG:
        if count == 0:
            count = reset
            maxVU = 0
        else:
            count-=1

        audio_data = audio.read(audio_channels * audio_samples * pasimple.format2width(audio_format))
        data = unpack("%dh" % (len(audio_data) / 2), audio_data)
        data = np.array(data, dtype='h')
        leftChannel  = data[0::2]
        rightChannel = data[1::2]

        newPeaks = [np.amax(leftChannel), np.amax(rightChannel)]
        CPeaks[0] *= decay
        CPeaks[0]  = newPeaks[0] if newPeaks[0] > CPeaks[0] else CPeaks[0]

        if newPeaks[0]>maxVU:
            maxVU  = newPeaks[0]
            #CPeaks = [0]*2
        
        volume     = MapValue(CPeaks[0], 0, maxVU, 0, 5000)
            
        pixelStep = checkStep(pixelStep)
        pixelColors, _ = guage(volume, pixelCount, pixelStep, subColorSpeed, 0, 5001)
        
        sendToServer(socket, message, pixelColors)

        pixelStep-=colorSpeed
        
    pixelColors = [(0,0,0)]*PIXELS
    
    sendToServer(socket, message, pixelColors)


def pixelCycle(message, step, colorSpeed, pixelPos, pixelSpeed, dim):
    socket      = createClientSocket(IP, PORT)
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

        sendToServer(socket, message, pixelColors)
    

def ClientManager(message):
    socket      = createClientSocket(IP, PORT)
    sendSetup(socket);
    
    while EXIT_SIG:
        #print("??")
        newMessageEvent.wait()
        with messageLock:
            messageCopy = message[:]
            message.clear()
            newMessageEvent.clear()
        sendMessage(socket, messageCopy)
        ConfirmationResponse(socket)

        
def main():    
    message    = []
    signal.signal(signal.SIGINT, handler)

    # Use Client thread when running remote
    # The thread will prevent the VU from hanging while the server replies
    # Also good for slow networks
    if SERVERMODE:
        clientThread = Thread(target=ClientManager, args=(message, ))
        clientThread.start()

    #pixelCycle(message, 255, 0, 8,  1, 50)      # message, stepStart, colorSpeed, pixelPos, pixelSpeed, dim    
    VUDFTRGB(message)                                 # CPU AVG. 40.0   NOW  9 - 12!!
    #VUDFTRGB3P(message)                               # CPU AVG. 39.3   NOW  9 - 12!!
    #VURGB(message, 0, -2, 17.4, .65, 4000)            # CPU AVG. 41.2   NOW  5 - 6.6
    
    RGB_OFF()
    
    
if __name__ == "__main__":
    main()
