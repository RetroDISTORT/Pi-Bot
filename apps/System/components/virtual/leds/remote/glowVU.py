import time
import sys
import numpy as np

from struct import unpack
from clientSocket import ClientSocket
from ledToolset import LedToolset


def VURGB(ip, port, pixelStep, colorSpeed, subColorSpeed, decay, reset):
    tools       = LedToolset()
    if (ip != "" and port != ""):
        tools.startClientThread(ip, int(port))
    else:
        tools.startClientThread()
    tools.createVU()
    
    pixelCount  = 16;
    pixelColors = [(0,0,0)]*pixelCount
    maxVU       = 0
    count       = reset
    CPeaks      = [0]*2
    color       = pixelStep

    while True:
        if count == 0:
            count = reset
            maxVU = 0
        else:
            count-=1

        leftChannel, rightChannel = tools.getChannelData()

        newPeaks = [np.amax(leftChannel), np.amax(rightChannel)]
        CPeaks[0] *= decay
        CPeaks[0]  = newPeaks[0] if newPeaks[0] > CPeaks[0] else CPeaks[0]

        if newPeaks[0]>maxVU:
            maxVU  = newPeaks[0]
        
        volume    = tools.MapValue(CPeaks[0], 0, maxVU, 0, 100)
        color     = tools.checkStep(color+colorSpeed)
        subColor  = color
        
        for i in range(pixelCount):
            subColor          = tools.checkStep(subColor)
            pixelColors[i], _ = tools.rainbow(subColor)
            pixelColors[i]    = tools.pixelBrightness(pixelColors[i], volume)
            subColor         += subColorSpeed

        tools.sendToServer(pixelColors)
            
        
def main(pixelStep, colorSpeed, subColorSpeed, decay, reset, ip = "", port = ""):    
    VURGB(ip, port, pixelStep, colorSpeed, subColorSpeed, decay, reset)
    
    
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
