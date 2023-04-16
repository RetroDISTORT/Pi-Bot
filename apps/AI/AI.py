import os               # Required for running command line functions
import sys              # Required for loading special modules
import time             # Required for delays
import configparser     # Required for ini files

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/display')
from menu     import Menu

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/processes')
from taskManager     import TaskManager


def mainMenu(menu, configurationFile):
    taskManager = TaskManager()
    config      = configparser.ConfigParser()
    #loadConfig(config, configurationFile)
    
    
    while True:
        select = menu.displayMenu(['Launcher', 'About', 'Exit'])
        if select == 'Launcher':
            launcherMenu(menu, taskManager)
        if select == 'About':
            menu.displayLargeMessage(["      Pi-Bot AI",
                                      "--------------------------",
                                      "       V 0.23.4.07",
                                      " Github: RetroDISTORT",
                                      "",
                                      "      [Click to Exit]"])
        if select == 'Exit':
            menu.displayOff()
            return


def launcherMenu(menu, taskManager):
    while True:
        menuOptions  = ['Face Test', 'Done'] 
        
        select = menu.displayMenu(menuOptions)

        if select == 'Face Test':
            taskManager.startTask('Face', 'AI', "python3 /opt/boobot/apps/AI/programs/faces.py")
            menu.displayLargeMessage(["     Face Test",
                                      " Simple AI oled test",
                                      " Starting Soon...",
                                      " [Click to Exit Test]"])
            taskManager.killType('Face')
        if select == 'Done':
            return


        
def main():
    configDirectory = "~/.boobot/AI"
    configFile      = "~/.boobot/WebApp/server.config"
    templateFile    = "/opt/boobot/apps/WebApp/configuration/server.config"
    
    #createConfig(configDirectory, configFile, templateFile)
    menu = Menu('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', 12)
    
    time.sleep(.5)
    mainMenu(menu, configFile)
    #mainMenu(menu, templateFile)


if __name__ == "__main__":
    main()
