import os               # Required for running command line functions
import sys              # Required for loading special modules
import time             # Required for delays
import socket           # required to get IP
import configparser     # Required for ini files

from signal import SIGKILL


sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/display')
from menu         import Menu

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/processes')
from taskManager  import TaskManager    


def mainMenu(menu):
    taskManager = TaskManager()
    
    while True:
        select = menu.displayMenu(['Stations', 'Volume', 'About', 'Exit'])
        
        if select == 'Stations':
            stationsMenu(menu, taskManager)
        if select == 'Volume':        
            serverMenu(menu, taskManager)
        if select == 'About':
            menu.displayLargeMessage(["      Pi-Bot Radio", "--------------------------", "       V 0.23.3.8", " Github: RetroDISTORT", "", "      [Click to Exit]"])
        if select == 'Exit':
            menu.displayOff()
            return


def stationsMenu(menu, taskManager):
    while True:
        selectedStation = menu.displayMenu(['Off'] + getStations('/opt/boobot/apps/Radio/Stations/') + ['Back'])
        if selectedStation != 'Back':
            #taskManager.killApplication('Radio')
            os.system("killall vlc")
            if selectedStation != 'Off':
                taskManager.startTask('Audio', 'Radio', "vlc /opt/boobot/apps/Radio/Stations/" + selectedStation)
        else:
            return


def getStations(dir):
    stationList = []
    
    for file in os.listdir(dir):
        appFolder = os.path.join(dir, file)
        nameIndex = appFolder.rindex('/')+1
        stationList.append(appFolder[nameIndex:])

    return stationList


def main():
    menu = Menu('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', 12)
    time.sleep(.5)
    mainMenu(menu)

    
if __name__ == "__main__":
    main()
