import os               # Required for running command line functions
import time             # Required for delays
import sys              # Required for loading special modules
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

#sys.path.insert(1, '/opt/boobot/src/components/server')
sys.path.insert(1, '/home/pi/Documents/boobot/src/components/virtual')

from menu     import Menu
    

def mainMenu(menu):
    while True:
        select = menu.displayMenu(['Start Server', 'Settings', 'Connection', 'About', 'Exit'])
        
        if select == 'Start Server':
            menu.displayMessage("This still not available.")
        if select == 'Settings':
            settingsMenu(menu)
        if select == 'Connection':
            menu.displayLargeMessage(["   Server Connection", "IP:", "Port(P):", "Port(S):", "Port(WS):", "      [Click to Exit]"])
        if select == 'About':
            menu.displayLargeMessage(["      Pi-Bot Server", "--------------------------", "       V 0.23.2.26", " Github: RetroDISTORT", "", "      [Click to Exit]"])
        if select == 'Exit':
            menu.displayOff()
            return

def settingsMenu(menu):
    while True:
        select = menu.displayMenu(['Enable Manual Access', 'Enable LEDS', 'Enable Screen', 'Enable Wheels M.', 'Enable Camera M.', 'Enable Speaker', 'Enable Camera', 'Enable Microphone', 'Done'])
        if select == 'Enable LEDS':
            menu.displayToggle("Enable:", ['True', 'False'], 0)
        if select == 'Enable Screen':
            menu.displayToggle("Enable:", ['True', 'False'], 0)
        if select == 'Enable Wheels M.':
            menu.displayToggle("Enable:", ['True', 'False'], 0)
        if select == 'Enable Camera M.':
            menu.displayToggle("Enable:", ['True', 'False'], 0)
        if select == 'Enable Speaker':
            menu.displayToggle("Enable:", ['True', 'False'], 0)
        if select == 'Enable Camera':
            menu.displayToggle("Enable:", ['True', 'False'], 0)
        if select == 'Enable Microphone':
            menu.displayToggle("Enable:", ['True', 'False'], 0)
        if select == 'Done':
            return

def main():
    menu = Menu('/opt/boobot/fonts/ratchet-clank-psp.ttf', 12)
    mainMenu(menu)


if __name__ == "__main__":
    main()
