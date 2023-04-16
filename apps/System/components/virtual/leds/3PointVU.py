import time
import sys
import numpy as np
from math import ceil as ceil

from struct import unpack

sys.path.insert(1,'/opt/boobot/apps/System/components/virtual/client')
from clientSocket import ClientSocket

sys.path.insert(1,'/opt/boobot/apps/System/components/virtual/leds')
from ledToolset import LedToolset


def VUDFTRGB3P(ip, port, pixelStep, colorSpeed, subColor, subColorSpeed, decay):
    tools       = LedToolset()
    pixelCount  = 16
    extra       = 1      #Prevents dead time due to slow buffer extraction

    value       = [0,0,0]
    levelPixels = [5,6,5]
    maxValue    = [5,5,5]
    color       = pixelStep

    if (ip != "" and port != ""):
        tools.startClientThread(ip, int(port))
    else:
        tools.startClientThread()
        
    tools.createVU()

    while True:
        leftChannel, _ = tools.getChannelData()
        
        newValues = tools.fft_3point(leftChannel)
           
        pixelColors = [(0,0,0)]*pixelCount
        brightness  = [[0],[0],[0]]
        #Update max values
        for i in range(3):
            maxValue[i] = newValues[i] if newValues[i] > maxValue[i] else maxValue[i]
        
        for i in range(3):
            value[i]         *= decay
            value[i]          = newValues[i] if newValues[i] > value[i] else value[i]
            #value       = maxValue
            brightness[i]     = tools.brightnessGuage(value[i], ceil(levelPixels[i]/2), -1, maxValue[i])
            if levelPixels[i]%2 == 0:
                brightness[i]     = brightness[i][::-1]
                brightness[i]    += brightness[i][::-1]
            else:
                brightness[i]     = brightness[i][::-1]
                brightness[i]    += brightness[i][1::-1]

        allBrightness = []
        
        for b in brightness:
            allBrightness += b
            
        color    = tools.checkStep(color + colorSpeed)
        subColor = color
        for pixel in range(pixelCount):
            pixelColors[pixel], subColor = tools.rainbow(subColor)
            pixelColors[pixel]           = tools.pixelBrightness(pixelColors[pixel], max(allBrightness[pixel],2))
            subColor                     = tools.checkStep(subColor + subColorSpeed)

        tools.sendToServer(pixelColors)
        
        
def main(pixelStep, colorSpeed, subColor, subColorSpeed, decay, ip = "", port = ""):
    VUDFTRGB3P(ip, port, pixelStep, colorSpeed, subColor, subColorSpeed, decay)
    
    
if __name__ == "__main__":
    if (len(sys.argv) == 8):
        main(float(sys.argv[3]),
             float(sys.argv[4]),
             float(sys.argv[5]),
             float(sys.argv[6]),
             float(sys.argv[7]),
             ip   = sys.argv[1],
             port = sys.argv[2] )
    else:
        main(float(sys.argv[1]),
             float(sys.argv[2]),
             float(sys.argv[3]),
             float(sys.argv[4]),
             float(sys.argv[5]))
