import time
import sys

sys.path.insert(1,'/opt/boobot/apps/System/components/virtual/client')
from clientSocket import ClientSocket

sys.path.insert(1,'/opt/boobot/apps/System/components/virtual/leds')
from ledToolset import LedToolset      
       
def RGB_OFF(ip, port):
    tools        = LedToolset()
    pixelCount   = 16;
    if (ip != "" and port != ""):
        tools.startClientThread(ip, int(port))
    else:
        tools.startClientThread()
        
    pixelColors = [(0,0,0)]*pixelCount
    
    tools.sendToServer(pixelColors)

        
def main(ip = "", port = ""):    
    RGB_OFF(ip, port)
    
    
if __name__ == "__main__":
    if (len(sys.argv) == 3):
        main(ip = sys.argv[1],
             port = sys.argv[2])
    else:
        main()
