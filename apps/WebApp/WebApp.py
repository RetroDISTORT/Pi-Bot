import os               # Required for running command line functions
import sys              # Required for loading special modules
import time             # Required for delays
import configparser     # Required for ini files

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/display')
#sys.path.insert(1, '/home/pi/Documents/boobot/apps/System/components/virtual/display')
from menu     import Menu

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/processes')
from taskManager     import TaskManager


def mainMenu(menu, configurationFile):
    taskManager = TaskManager()
    config      = configparser.ConfigParser()
    loadConfig(config, configurationFile)
    
    while True:
        select = menu.displayMenu(['Launcher', 'Settings', 'Connection', 'About', 'Exit'])
        if select == 'Launcher':
            launcher(menu, taskManager, config, configurationFile)
        if select == 'Settings':
            settingsMenu(menu, config)
            saveConfig(config, configurationFile)
        if select == 'Connection':
            serverMenu(menu, taskManager, config)
        if select == 'About':
            aboutMenu(menu)
        if select == 'Exit':
            menu.displayOff()
            return
        
        
def settingsMenu(menu, configuration):
    menuOptions = [[option.title(), configuration['Settings'].getboolean(option)] for option in configuration.options('Settings')]
    menuOptions.append('Done')
    
    while True:
        select, menuOptions = menu.displayMenu(menuOptions, True)

        if select == 'Done':
            return
        else:
            configuration['Settings'][select] = str(not configuration['Settings'].getboolean(select))
            menuOptions[0][1] = configuration['Settings'].getboolean(select) # Update menu options
        

def getIP(ip):
    if ip!="":
        return ip
    try:
        return os.popen("hostname -I").read().split()[0]
    except:
        return "IP ERROR"


def launcher(menu, taskManager, configuration, configurationFile):
    while True:
        website      = len(taskManager.listType('Website')) >= 1
        menuOptions  = ['Kill WebApp', 'Done'] if website  else ['Start WebApp', 'Done']
        select       = menu.displayMenu(menuOptions)

        if select == 'Start WebApp':
            startWebApp(menu, taskManager, configuration, configurationFile)
        if select == 'Kill WebApp':
            taskManager.killType('Website', True)
        
        if select == 'Done':
            return


def startWebApp(menu, taskManager, configuration, configurationFile):
    section, ip, portW, portWS, portS = connectionInfo(configuration)
    
    if configuration['Settings'].getboolean('webrtc'):
        if len(taskManager.listType('WebSocketServer')) < 1:
            menu.displayMessage("Starting SServer")
            taskManager.startTask('SocketServer', 'WebApp', "python3 /opt/boobot/apps/System/programs/launchServerSocket.py", True)
        taskManager.startTask('Website', 'WebApp', "python3 /opt/boobot/apps/WebApp/Website/websiteWebRTC.py  --config-file " + os.path.expanduser(configurationFile), True)
    else:
        if len(taskManager.listType('WebSocketServer')) < 1:
            menu.displayMessage("Starting WServer")
            taskManager.startTask('WebSocketServer', 'WebApp', "python3 /opt/boobot/apps/System/programs/launchServerWebSocket.py", True)
        taskManager.startTask('Website', 'WebApp', "python3 /opt/boobot/apps/WebApp/Website/websiteNoWebRTC.py --config-file " + os.path.expanduser(configurationFile), True)

    #webpage = ip+":"+portW if section=='WebsiteLocal' else ip
    
    menu.displayLargeMessage(["   Server Connection",
                              "Using: "+section,
                              "Open a web browser",
                              "go to:", str(ip),
                              "port:", str(portW),
                              "portWS:", str(portWS),
                              "portS:", str(portS),
                              "","      [Click to Exit]"])

    if configuration['Settings'].getboolean('quick exit'):
        taskManager.killType('WebSocketServer', True)
        taskManager.killType('SocketServer', True)
        taskManager.killType('Website', True)
    

def serverMenu(menu, taskManager, configuration):
    while True:
        WSServer     = len(taskManager.listType('WebSocketServer')) >= 1
        SServer      = len(taskManager.listType('SocketServer')) >= 1
        menuOptions  = ['Server info', 'Back']
        menuOptions += ['Kill WS Server'] if WSServer else ['Start WS Server']
        menuOptions += ['Kill S Server']  if SServer  else ['Start S Server']
        select = menu.displayMenu(menuOptions)
    
        if select == 'Start WS Server':
            if menu.displayToggle("Enable:", ['True', 'False'], 0) == 'True':
                taskManager.startTask('WebSocketServer', 'WebApp', "python3 /opt/boobot/apps/System/programs/launchServerWebSocket.py", True)

        if select == 'Start S Server':
            if menu.displayToggle("Enable:", ['True', 'False'], 0) == 'True':
                taskManager.startTask('SocketServer', 'WebApp', "python3 /opt/boobot/apps/System/programs/launchServerSocket.py", True)

        if select == 'Kill S Server':
            taskManager.killType('SocketServer', True)

        if select == 'Kill WS Server':
            taskManager.killType('WebSocketServer', True)

        if select == 'Connection info':
            section, ip, portW, portWS, portS = connectionInfo(configuration)
            menu.displayLargeMessage(["   Server Connection", "IP:"+ip, "Port(A):"+portW, "Port(S):"+portS, "Port(WS):"+portWS, "      [Click to Exit]"])
                
        if select == 'Back':
            return

        
def connectionInfo(configuration):
    section = 'WebsiteLocal' if configuration['Settings'].getboolean('local settings') else 'WebsiteRemote'
    ip      = getIP(configuration[section]['ip'])
    portW   =       configuration[section]['Port']
    portWS  =       configuration[section]['websocketport']
    portS   =       configuration['Socket']['Port']

    return section, ip, portW, portWS, portS        

        
def createConfig(configurationDirectory, configurationFile, templateFile):
    createFolder    = "mkdir -p " + configurationDirectory
    copyTemplate    = "cp " + templateFile + " " + configurationFile

    os.system(createFolder)

    if not os.path.isfile(os.path.expanduser(configurationFile)):
        os.system(copyTemplate)

        
def loadConfig(configuration, fileName):
    configuration.read(os.path.expanduser(fileName))
    return

def saveConfig(configuration, fileName):
    with open(os.path.expanduser(fileName), 'w') as configfile:
        configuration.write(configfile)
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
                                      "       V 0.23.4.12",
                                      " Github: RetroDISTORT",
                                      "",
                                      "      [Click to Exit]"])
        if select == 'Common Errors':
            menu.displayLargeMessage(["Website Error:",
                                      "Mic Busy:",
                                      "System>Status>Mic",
                                      "Programs that may be",
                                      "using the mic:"
                                      "ps aux | grep pulseaudio"])
        if select == 'Back':
            return


def main():
    configDirectory = "~/.boobot/WebApp"
    configFile      = "~/.boobot/WebApp/app.config"
    templateFile    = "/opt/boobot/apps/WebApp/configuration/app.config"
    
    createConfig(configDirectory, configFile, templateFile)
    menu = Menu('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', 12)
    
    time.sleep(.5)
    mainMenu(menu, configFile)


if __name__ == "__main__":
    main()
