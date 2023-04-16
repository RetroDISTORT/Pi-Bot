import os               # Required for running command line functions
import time             # Required for delays
import sys              # Required for loading special modules
import random
import math

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

#sys.path.insert(1, '/opt/boobot/src/components/server')
sys.path.insert(1,'/home/pi/Documents/boobot/apps/System/components/virtual/display')
from canvas        import Canvas


def graphRandom():
    array = [random.random() for i in range(50)] #initial array
    graph = Canvas()
    while(True):
        array.append(random.random())
        array.pop(0)
        graph.addGraph(0,0,128,64,array)
        graph.drawCanvas()


def graphSine():
    speed  = 10
    points = 7.9
    array  = [0]*50 #initial array
    graph  = Canvas()
    x      = 0; 
    while(True):
        x+=speed
        if x >= 360:
            x = x%360
        array.append(math.sin(math.radians(x)))
        array.pop(0)

        graph.addRectangle(0,16,127,32,255)
        graph.addLine(0,32,127,0)
        graph.addLine(64,16,0,32)
        graph.addText(0,50,"This is the pow(of, sin!)")
        graph.addGraph(0,16,128,32,array)
        graph.drawCanvas()

    
if __name__ == "__main__":
    graphRandom()
    #graphSine()
