import os               # Required for running command line functions
import sys              # Required for loading special modules
import time             # Required for delays
import configparser     # Required for ini files

sys.path.insert(1, '/home/pi/Documents/boobot/apps/System/components/virtual/display')
from menu     import Menu

sys.path.insert(1, '/home/pi/Documents/boobot/apps/System/components/virtual/processes')
from taskManager     import TaskManager


def mainMenu(menu):
    fileName    = '/opt/boobot/apps/WebApp/server.config'
    taskManager = TaskManager()
    config      = configparser.ConfigParser()
    loadConfig(config, fileName)
    
    
    while True:
        select = menu.displayMenu(['Launcher', 'Settings', 'Connection', 'About', 'Exit'])
        
        if select == 'Launcher':
            #menu.displayMessage("This still not available.")
            launcher(menu, taskManager, config)
        if select == 'Settings':
            settingsMenu(menu)
        if select == 'Connection':
            menu.displayLargeMessage(["   Server Connection", "IP:"+getIP(), "Port(A):"+config['Website']['Port'], "Port(S):"+config['Socket']['Port'], "Port(WS):"+config['Websocket']['Port'], "      [Click to Exit]"])
        if select == 'About':
            aboutMenu(menu)
        if select == 'Exit':
            menu.displayOff()
            return


def aboutMenu(menu):
    while True:
        select = menu.displayMenu(['\"Quick Exit\"', 'Why a server?', 'WebApp', 'Back'])
        
        if select == '\"Quick Exit\"':
            menu.displayLargeMessage(["    <<QUICK EXIT>>",
                                      "Quick exit lets you end",
                                      "the server and webapp",
                                      "instantly by pressing",
                                      "the square button.",
                                      "This mode is strongly",
                                      "recommended for",
                                      "privacy.",
                                      "",
                                      "   [click to continue]"])

        if select == 'Why a server?':
            menu.displayLargeMessage(["    <<Server>>",
                                      "The server enables",
                                      "the webapp controls.",
                                      "",
                                      "This opens a socket",
                                      "and a websocket.",
                                      "The webapp only uses",
                                      "the websocket.",
                                      "   [click to continue]"])
        if select == 'WebApp':
            menu.displayLargeMessage(["      Pi-Bot Server",
                                      "--------------------------",
                                      "       V 0.23.2.26",
                                      " Github: RetroDISTORT",
                                      "",
                                      "      [Click to Exit]"])
        if select == 'Back':
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


def getIP():
    return os.popen("hostname -I").read().split()[0]


def launcher(menu, taskManager, configuration):
    while True:
        server       = taskManager.listType('Server')
        website      = taskManager.listType('Website')
        menuOptions  = ['Start WebApp']         if len(website) == 0 else ['Kill WebApp']
        menuOptions += ['Start Server', 'Done'] if len(server)  == 0 else ['Kill Server', 'Done']
        
        select = menu.displayMenu(menuOptions)

        if select == 'Start WebApp':
            startWebApp(menu, taskManager, configuration, server)
        if select == 'Kill WebApp':
            taskManager.killType('Website')
        if select == 'Start Server':
            taskManager.startTask('Server', 'WebApp', "sudo python3 /opt/boobot/apps/System/programs/Server.py")
        if select == 'Kill Server':
            taskManager.killType('Server')
        if select == 'Done':
            return


def startWebApp(menu, taskManager, configuration, serverStatus):
    quickExit = menu.displayToggle("Enable Quick Exit:", ['Yes', 'No'], 0)

    if len(serverStatus) == 0:    
        if menu.displayToggle("Enable Server:", ['Yes', 'No'], 0) == 'Yes':
            taskManager.startTask('Server', 'WebApp', "python3 /opt/boobot/apps/System/programs/Server.py")
            
    taskManager.startTask('Website', 'WebApp', "python3 /opt/boobot/apps/WebApp/Website/website.py")
    menu.displayLargeMessage(["   Server Connection",
                              "Open a web browser",
                              "go to:", getIP() + ":" + configuration['Website']['Port'],
                              "      [Click to Exit]"])
    
    if quickExit == 'Yes':
        taskManager.killType('Server')
        taskManager.killType('Website')
    
        

def loadConfig(configuration, fileName):
    configuration.read(fileName)
    return

        
def main():
    menu = Menu('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', 12)
    
    time.sleep(.5)
    mainMenu(menu)


if __name__ == "__main__":
    main()
