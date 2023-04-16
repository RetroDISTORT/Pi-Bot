import time
import sys
import errno       # Required for sockets
import signal      # Required for handler
import socket      # Required for getIP()
import pasimple
import numpy as np

from math import ceil as ceil
from struct import unpack
from threading import Thread, Event, Lock

sys.path.insert(1,'/opt/boobot/apps/System/components/virtual/client')
from clientSocket import ClientSocket


class LedToolset:
    def __init__(self):
        self.pixels           = 16
        self.port             = 9001
        #self.delay            = 1/audio_updates
        self.headerSize       = 10
        self.IP               = "10.0.0.17"
        #self.PORT             = 9001
        #self.confirmation     = True
        self.brightness       = .1


    def startClientThread(self, ip = "", port = 9001):
        self.ip               = self.getIP(ip)
        self.port             = port
        self.message          = []
        self.messageLock      = Lock()
        self.newMessageEvent  = Event()
        self.newMessageEvent.clear()

        self.clientThread     = Thread(target=self.ClientManager)
        self.clientThread.start()

        #signal.signal(signal.SIGINT, handler)


    def getIP(self, IP):
        if (IP == ""):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            IP = s.getsockname()[0]
            
        return IP
    
        
    def sendToServer(self, pixelColors):
        #print(pixelColors)
        with self.messageLock:
            self.message.clear()
            self.message += pixelColors[:]
            self.newMessageEvent.set()
    
            
    def ClientManager(self):
        socket = ClientSocket(self.ip, self.port)
        
        while True:#EXIT_SIG:
            self.newMessageEvent.wait()
            with self.messageLock:
                messageCopy = self.message[:]
                self.message.clear()
                self.newMessageEvent.clear()
    
            pixelData = [list(pixel) for pixel in messageCopy]
            jsonMessage = ('{"device":  "LED",'
                           '"command": "setPixels",'
                           '"colors":' + str(pixelData) +
                           '}')
            socket.send(jsonMessage)
            socket.recieve()        

            
    def checkStep(self, step):
        if step > 765:             # RESET TO A STATE IN RANGE
            step = step - 765
        if 0 > step:
            step = 765 + step
            
        return step

    
    def rainbow(self, step):
        step = self.checkStep(step)
        
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
    
    
    def pixelBrightness(self, pixel, percentage):
        #Assuming the current color is max value
        dimmedColors =[]
        for maxColor in range(len(pixel)):
            dimmedColor = int(self.MapValue(percentage, 0, 100, 0, pixel[maxColor]))
            dimmedColors.append(dimmedColor)
    
        return tuple(dimmedColors)
    
    
    def dimPixels(self, pixelColors, dim):
        for pixel in range(len(pixelColors)):
            dimmedColors = []
            
            for color in range(len(pixelColors[pixel])):
                dimmedColors.append(int(pixelColors[pixel][color]-dim if pixelColors[pixel][color]-dim>0 else 0))
                
            pixelColors[pixel] = tuple(dimmedColors)
    
        return pixelColors
    
    
    # Traceback (most recent call last):
    #   File "/opt/boobot/apps/System/components/virtual/leds/VU.py", line 361, in <module>
    #     main(float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]))
    #   File "/opt/boobot/apps/System/components/virtual/leds/VU.py", line 355, in main
    #     VURGB(message, pixelStep, colorSpeed, subColorSpeed, decay, reset)             # CPU AVG. 41.2   NOW  5 - 6.6
    #   File "/opt/boobot/apps/System/components/virtual/leds/VU.py", line 337, in VURGB
    #     pixelColors, _ = guage(volume, pixelCount, pixelStep, subColorSpeed, 0, 5001)
    #   File "/opt/boobot/apps/System/components/virtual/leds/VU.py", line 144, in guage
    #     pixelColors[pixel], pixelStep = rainbow(pixelStep)
    # IndexError: list assignment index out of range
    
    def guage(self, value, pixels, pixelStep, colorSpeed, minValue, maxValue):
        pixelColors         = [(0,0,0)]*pixels
        lastColor           = [(0,0,0)]
        pixelsOn            = self.MapValue(value, minValue, maxValue, 0, pixels)
        lastPixelBrightness = (pixelsOn-int(pixelsOn))*100

        for pixel in range(ceil(pixelsOn)):
            pixelColors[pixel], pixelStep = self.rainbow(pixelStep)
            pixelStep   += colorSpeed
    
        if lastPixelBrightness != 0:
            pixelColors[ceil(pixelsOn)-1] = self.pixelBrightness(pixelColors[ceil(pixelsOn)-1], lastPixelBrightness)
                
        return pixelColors, pixelStep
    
    
    def brightnessGuage(self, value, pixels, minValue, maxValue):
        brightness          = [0]*pixels
        pixelsOn            = self.MapValue(value, minValue, maxValue, 0, pixels)
        lastPixelBrightness = (pixelsOn-int(pixelsOn))*100
    
        for pixel in range(ceil(pixelsOn)):
            brightness[pixel] = 100
    
        if lastPixelBrightness != 0:
            brightness[ceil(pixelsOn)-1] = lastPixelBrightness
    
        return brightness
    
    ####################
    # VU METER METHODS ######################################################################################################
    ####################
    
    def createVU(self,
                 audio_server    = None,
                 audio_device    = "0",
                 audio_channels  = 2,
                 audio_rate      = 48000,
                 audio_direction = pasimple.PA_STREAM_RECORD,
                 audio_format    = pasimple.PA_SAMPLE_S16LE,
                 audio_app_name  = 'pythonVU',
                 audio_stream    = None,
                 audio_updates   = 30):

        self.audio_channels  = audio_channels
        self.audio_rate      = audio_rate
        self.audio_format    = audio_format
        self.audio_samples   = int(audio_rate/audio_updates)*2
        self.audio           = pasimple.PaSimple(audio_direction, audio_format, audio_channels, audio_rate, app_name=audio_app_name, stream_name=audio_stream, server_name=audio_server, device_name=audio_device)


    def readVU(self):
        return self.audio.read(self.audio_channels * self.audio_samples * pasimple.format2width(self.audio_format))


    def getChannelData(self):
        audio_data = self.readVU()
        audio_data = audio_data[:int(len(audio_data))]
        data = unpack("%dh" % (len(audio_data) / 2), audio_data)
        data = np.array(data, dtype='h')
        leftChannel = data[0::2]
        rightChannel = data[1::2]
        return leftChannel, rightChannel

    
    def endVU(self):
        self.audio.close()

    
    ###############
    # OTHER TOOLS ###########################################################################################################
    ###############
    
    def MapValue(self, value, fromMinimum, fromMaximum, toMinimum, toMaximum):
        value = max(fromMinimum,min(fromMaximum,value))
        if value==fromMaximum:
            return toMaximum #Rounding in the last line may cause it to return a greater value
        if value==fromMinimum:
            return toMinimum
        
        inMax     = abs(fromMinimum-fromMaximum)
        outMax    = abs(toMinimum-toMaximum)
        newValue  = value - fromMinimum 
        output    = 0 if inMax==0 else (newValue*outMax/inMax)+toMinimum
        
        return max(toMinimum,min(toMaximum,output))
    
    
    def power_index(self, val):
        return int(2 * int(self.audio_samples) * val / self.audio_rate)
    
    
    def fft_3point(self, data):
        matrix    = [0, 0, 0]
        weighting = [    1,   8,   16]
        ranges    = [0, 200, 1000, 8000]
    
        fourier = np.fft.rfft(data)
        fourier = np.delete(fourier, len(fourier) - 1)
    
        #print(len(fourier))
        power = np.abs(fourier)
        for i in range(len(ranges)-1):
            matrix[i] = int(np.mean(power[self.power_index(ranges[i]) : self.power_index(ranges[i+1]) :1]))
        
        #matrix = np.divide(np.multiply(matrix, weighting), 100000)
        #matrix = matrix.clip(1)
        matrix = [float(m) for m in matrix]
        return matrix
        
    
    def compute_fft(self, data):
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
            matrix[i] = int(np.mean(power[self.power_index(ranges[i]) : self.power_index(ranges[i+1]) :1]))
        
        
        matrix = np.divide(np.multiply(matrix, weighting), 100000)#10000000000)
        #matrix = matrix.clip(1)
        matrix = [float(m) for m in matrix]
        return matrix
    
    
    def VUSampleLE(self):
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
    
        
    def VUFFT(self):
        audio = CreateVU()
        while EXIT_SIG:
            audio_data = audio.read(audio_channels * audio_samples * pasimple.format2width(audio_format))
            data = unpack("%dh" % (len(audio_data) / 2), audio_data)
            data = np.array(data, dtype='h')
            leftChannel = data[0::2]
            bins = compute_fft(leftChannel)
            print(bins)
            
        EndVU(audio)
    
