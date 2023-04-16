import time
import sys
from clientSocket import ClientSocket
from ledToolset import LedToolset      


def colorGlowCycle(ip, port, pixelStep, speed, brightnessChange, brightness):
    tools       = LedToolset()
    if (ip != "" and port != ""):
        tools.startClientThread(ip, int(port))
    else:
        tools.startClientThread()
    
    pixelCount  = 16
    pixelColors = [(0,0,0)]

    while True:
        time.sleep(.01)
        tools.sendToServer(pixelColors)
        
        brightness += brightnessChange;
        if not (0 <= brightness and brightness <= 100):
            brightnessChange = -brightnessChange
            brightness = 0 if brightness < 0 else 100

        pixelStep += speed
        pixelColors[0], pixelStep = tools.rainbow(pixelStep)
        pixelColors[0]            = tools.pixelBrightness(pixelColors[0], brightness)

        
def main(stepStart, colorSpeed, glowSpeed, brightness, ip = "", port = ""):
    colorGlowCycle(ip, port, stepStart, colorSpeed, glowSpeed, brightness)
    
    
if __name__ == "__main__":
    if (len(sys.argv) == 7):
        main(float(sys.argv[3]),
             float(sys.argv[4]),
             float(sys.argv[5]),
             float(sys.argv[6]),
             ip   = sys.argv[1],
             port = sys.argv[2] )
    else:
        main(float(sys.argv[1]),
             float(sys.argv[2]),
             float(sys.argv[3]),
             float(sys.argv[4]))
