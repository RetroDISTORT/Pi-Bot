import time
import sys
import numpy as np
from math import ceil as ceil

from struct import unpack

sys.path.insert(1,'/opt/boobot/apps/System/components/virtual/client')
from clientSocket import ClientSocket

sys.path.insert(1,'/opt/boobot/apps/System/components/virtual/leds')
from ledToolset import LedToolset


def VUDFTRGB(ip, port, pixelStep, colorSpeed, subColor, subColorSpeed, decay, reset):
    tools       = LedToolset()
    
    pixelCount  = 16
    bins        = pixelCount
    
    brightness  = [0]*pixelCount
    extra       = 1      #Prevents dead time
    resetCount  = 0
    VUMax       = 0
    boost       = .01

    if (ip != "" and port != ""):
        tools.startClientThread(ip, int(port))
    else:
        tools.startClientThread()
        
    tools.createVU()
    
    while True:
        leftChannel, _ = tools.getChannelData()
        
        pixelColors = [(0,0,0)]*pixelCount
        VULevels = tools.compute_fft(leftChannel)

        if resetCount > reset:
            resetCount = 0
            VUMax = 0
            
        VUMax = VUMax if VUMax > max(VULevels) else max(VULevels)

        pixelStep += colorSpeed
        pixelStep  = tools.checkStep(pixelStep)
        subColor   = pixelStep
        for i in range(16):
            brightness[i] *= decay
            brightness[i]  = VULevels[i] if VULevels[i] > brightness[i] else brightness[i]
            VULevels[i]    = VULevels[i] if VULevels[i]*boost >= VUMax else VULevels[i]*boost #have more leds reach max

            subColor   += subColorSpeed
            pixelColors[i], _ = tools.rainbow(subColor) # Rainbow color

            #pixelColors[i], pixelStep = rainbow(int(MapValue(VULevels[i], 0, VUMax, 0, 255))) # Intensity

            pixelColors[i] = tools.pixelBrightness(pixelColors[i], tools.MapValue(brightness[i], 0, VUMax, 0, 100))

        tools.sendToServer(pixelColors)
    
        
def main(pixelStep, colorSpeed, subColor, subColorSpeed, decay, reset, ip = "", port = ""):    
    VUDFTRGB(ip, port, pixelStep, colorSpeed, subColor, subColorSpeed, decay, reset)
    
if __name__ == "__main__":
    if (len(sys.argv) == 9):
        main(float(sys.argv[3]),
             float(sys.argv[4]),
             float(sys.argv[5]),
             float(sys.argv[6]),
             float(sys.argv[7]),
             float(sys.argv[8]),
             ip   = sys.argv[1],
             port = sys.argv[2] )
    else:
        main(float(sys.argv[1]),
             float(sys.argv[2]),
             float(sys.argv[3]),
             float(sys.argv[4]),
             float(sys.argv[5]),
             float(sys.argv[6]))
    
