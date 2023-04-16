import time
import sys

from clientSocket import ClientSocket
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
