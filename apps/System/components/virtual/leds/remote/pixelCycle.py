import time
import sys

from clientSocket import ClientSocket
from ledToolset import LedToolset      


def pixelCycle(ip, port, pixelStep, colorSpeed, pixelPos, pixelSpeed, dim):
    tools        = LedToolset()
    pixelCount   = 16
    pixelColors  = [(0,0,0)]*pixelCount    

    if (ip != "" and port != ""):
        tools.startClientThread(ip, int(port))
    else:
        tools.startClientThread()

    while True:
        time.sleep(.01)
        pixelStep += colorSpeed
        pixelPos  += pixelSpeed
        
        if pixelPos>=pixelCount:
            pixelPos = pixelPos%pixelCount;
        if pixelPos<0:
            pixelPos = pixelPos%pixelCount;
        
        pixelColors = tools.dimPixels(pixelColors, dim)
        pixelColors[int(pixelPos)], pixelStep = tools.rainbow(pixelStep)
        tools.sendToServer(pixelColors)

        
def main(stepStart, colorSpeed, glowSpeed, pixelSpeed, brightness, ip = "", port = ""):
    pixelCycle(ip, port, stepStart, colorSpeed, glowSpeed, pixelSpeed, brightness)
    
    
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
