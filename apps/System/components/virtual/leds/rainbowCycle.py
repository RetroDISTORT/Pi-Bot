import time
import sys

sys.path.insert(1,'/opt/boobot/apps/System/components/virtual/client')
from clientSocket import ClientSocket

sys.path.insert(1,'/opt/boobot/apps/System/components/virtual/leds')
from ledToolset import LedToolset


def rainbowCycle(ip, port, speed):
    tools       = LedToolset()
    pixelCount  = 16;
    pixelColors = [(0,0,0)]*pixelCount
    pixelStep   = [(i*765/pixelCount) for i in range(pixelCount)]

    if (ip != "" and port != ""):
        tools.startClientThread(ip, int(port))
    else:
        tools.startClientThread()
    
    while True:
        time.sleep(.01)
        tools.sendToServer(pixelColors)
        for i in range(pixelCount):
            pixelStep[i] += speed
            pixelColors[i], pixelStep[i] = tools.rainbow(pixelStep[i])

        
def main(colorSpeed, ip = "", port = ""):    
    rainbowCycle(ip, port, colorSpeed)
    
    
if __name__ == "__main__":
    if (len(sys.argv) == 4):
        main(float(sys.argv[3]),
             ip   = sys.argv[1],
             port = sys.argv[2] )
    else:
        main(float(sys.argv[1]))
