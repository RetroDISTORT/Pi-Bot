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
    maxVU       = 0
    count       = 0
    CPeaks      = [0]*2
    volume      = [0]*2
    
    while True:
        if count == 0:
            count = reset
            maxVU = 0
        else:
            count-=1

        leftChannel, rightChannel = tools.getChannelData()

        newPeaks   = [np.amax(leftChannel), np.amax(rightChannel)]

        for channel in [0,1]:
            CPeaks[channel] *= decay
            CPeaks[channel]  = newPeaks[channel] if newPeaks[channel] > CPeaks[channel] else CPeaks[channel]

            if newPeaks[channel]>maxVU:
                maxVU  = newPeaks[channel]
        
            volume[channel] = tools.MapValue(CPeaks[channel], 0, maxVU, 0, 5000)

        pixelStep = tools.checkStep(pixelStep)
        pixelColors1, _ = tools.guage(volume[0], int(pixelCount/2), pixelStep, subColorSpeed, 0, 5001)
        pixelColors2, _ = tools.guage(volume[1], int(pixelCount/2), pixelStep, subColorSpeed, 0, 5001)
        pixelColors     = [pixelColors1[0]] if volume[0] > volume[1] else [pixelColors2[0]]
        pixelColors    += pixelColors1[1:9]
        pixelColors    += [pixelColors1[7]] if volume[0] > volume[1] else [pixelColors2[7]]
        pixelColors    += pixelColors2[8:0:-1]

        tools.sendToServer(pixelColors)

        pixelStep-=colorSpeed
    
        
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
