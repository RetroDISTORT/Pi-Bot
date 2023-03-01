import os               # Required for running command line functions
import time             # Required for delays
import sys              # Required for loading special modules

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

#sys.path.insert(1, '/opt/boobot/src/components/server')
sys.path.insert(1, '/home/pi/Documents/boobot/src/components/virtual')

from menu     import Menu
    

def mainMenu():
    menu = Menu('/opt/boobot/fonts/ratchet-clank-psp.ttf', 12)
    menu.displayMenu(['Option1', 'Option2', 'Option3', 'Option4'])
    print(menu.displayToggle("Enable:", ['True', 'False'], 0))
    menu.displayMessage("Long scrolling sample message")
    menu.displayOff()

def main():   
    mainMenu()


if __name__ == "__main__":
    main()
