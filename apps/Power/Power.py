import os               # Required for running command line functions
import time             # Required for delays
import sys              # Required for loading special modules

sys.path.insert(1, '/home/pi/Documents/boobot/apps/System/components/virtual/display')
from menu     import Menu

def mainMenu(menu):
    while True:
        select = menu.displayMenu(['Shutdown', 'Restart', 'Cancel'])
        
        if select == 'Shutdown':
            menu.displayOff()
            os.system("sudo shutdown now")
        if select == 'Restart':
            menu.displayOff()
            os.system("sudo reboot now")
        if select == 'Cancel':
            return

def main():
    menu = Menu('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', 12)
    time.sleep(.5)
    mainMenu(menu)
    
if __name__ == "__main__":
    main()
