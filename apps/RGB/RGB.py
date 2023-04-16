import os               # Required for running command line functions
import time             # Required for delays
import sys              # Required for loading special modules
import configparser     # Required for ini files


sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/display')
from menu     import Menu

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/processes')
from taskManager     import TaskManager


stepStart     = "0"
colorSpeed    = "4"
glowSpeed     = "3"
pixelSpeed    = ".1"
brightness    = "3"
subColor      = "0"
subColorSpeed = "50"
decay         = ".80"  # VU meter peak decay
reset         = "4000" # Steps until VU meter max peak reset


def mainMenu(menu, configurationFile):
    appConfig      = configparser.ConfigParser()
    taskManager    = TaskManager()
    loadConfig(appConfig, configurationFile)
    modeMenu(menu, appConfig, taskManager, getIP(), appConfig['Socket']['port'])
    while True:
        select = menu.displayMenu(['Modes', 'Settings', 'Server', 'About', 'Exit'])
        
        if select == 'Modes':
            modeMenu(menu, appConfig, taskManager, getIP(), appConfig['Socket']['port'])
        if select == 'Settings':
            settingsMenu(menu, appConfig, configurationFile)
        if select == 'Server':
            serverMenu(menu, taskManager)
        if select == 'About':
            menu.displayLargeMessage(["      Pi-Bot Server", "--------------------------", "       V 0.23.3.28", " Github: RetroDISTORT", "", "      [Click to Exit]"])
        if select == 'Exit':
            menu.displayOff()
            return

        
def serverMenu(menu, taskManager):
    while True:
        WSServer     = len(taskManager.listType('WebSocketServer')) >= 1
        SServer      = len(taskManager.listType('SocketServer')) >= 1
        menuOptions  = ['Server info', 'Back']
        menuOptions += ['Kill WS Server'] if WSServer else ['Start WS Server']
        menuOptions += ['Kill S Server']  if SServer  else ['Start S Server']
        select = menu.displayMenu(menuOptions)
    
        if select == 'Start WS Server':
            if menu.displayToggle("Enable:", ['True', 'False'], 0) == 'True':
                taskManager.startTask('WebSocketServer', 'RGB', "python3 /opt/boobot/apps/System/programs/launchServerWebSocket.py", True)

        if select == 'Start S Server':
            if menu.displayToggle("Enable:", ['True', 'False'], 0) == 'True':
                taskManager.startTask('SocketServer', 'RGB', "python3 /opt/boobot/apps/System/programs/launchServerSocket.py", True)

        if select == 'Kill S Server':
            taskManager.killType('SocketServer', True)

        if select == 'Kill WS Server':
            taskManager.killType('WebSocketServer', True)

        if select == 'Server info':
            menu.displayLargeMessage(["   Server Connection", "IP: "+getIP(), "Port(WS): 9000", "Port(S): 9001", "", "      [Click to Exit]"])
                
        if select == 'Back':
            return

        
def settingsMenu(menu, configuration, fileName):
    while True:
        select = menu.displayMenu(['Reset All', 'Exit'])
        if select == 'Reset All':
            createConfig(configuration)
            saveConfig(configuration, fileName)
            
        if select == 'Exit':
            menu.displayOff()
            return

        
def modeMenu(menu, config, taskManager, ip, port):
    if len(taskManager.listType('SocketServer')) == 0:
        menu.displayMessage("Server is off")
        return
    
    select = menu.displayMenu(['Off', 'Glow Cycle', 'Pixel Cycle', 'Rainbow Cycle', 'VU', 'VU Stereo', '3 Point VU', 'Spectrum', 'Glow VU', 'Back'])
    if select != 'Back':
        taskManager.killType('LED')


    if select == 'Off':
        taskManager.startTask('LED', 'RGB', "python3 /opt/boobot/apps/System/components/virtual/leds/off.py ")
        menu.displayMessage("Close once LEDs are off...")
        taskManager.killType('LED')
        
        
    if select == 'Glow Cycle':
        taskManager.startTask('LED', 'RGB', "python3 /opt/boobot/apps/System/components/virtual/leds/colorGlowCycle.py " +
                              ip    + " " +
                              port  + " " +
                              config['GlowCycle:Default']['stepStart']  + " " +
                              config['GlowCycle:Default']['colorSpeed'] + " " +
                              config['GlowCycle:Default']['glowSpeed']  + " " +
                              config['GlowCycle:Default']['brightness'] )

    if select == 'Pixel Cycle':
        taskManager.startTask("LED", "RGB", "python3 /opt/boobot/apps/System/components/virtual/leds/pixelCycle.py " +
                              ip    + " " +
                              port  + " " +
                              config['PixelCycle:Default']['stepStart']  + " " +
                              config['PixelCycle:Default']['colorSpeed'] + " " +
                              config['PixelCycle:Default']['glowSpeed']  + " " +
                              config['PixelCycle:Default']['pixelSpeed'] + " " +
                              config['PixelCycle:Default']['brightness'] )
        
    if select == 'Rainbow Cycle':
        taskManager.startTask("LED", "RGB", "python3 /opt/boobot/apps/System/components/virtual/leds/rainbowCycle.py " +
                              ip    + " " +
                              port  + " " +
                              colorSpeed )
        
    if select == 'VU':
        taskManager.startTask("LED", "RGB", "python3 /opt/boobot/apps/System/components/virtual/leds/VU.py " +
                              ip    + " " +
                              port  + " " +
                              config['VU:Default']['stepStart']      + " " +
                              config['VU:Default']['colorSpeed']     + " " +
                              config['VU:Default']['subColorSpeed']  + " " +
                              config['VU:Default']['decay']          + " " +
                              config['VU:Default']['reset'])

    if select == 'VU Stereo':
        taskManager.startTask("LED", "RGB", "python3 /opt/boobot/apps/System/components/virtual/leds/VUStereo.py " +
                              ip    + " " +
                              port  + " " +
                              config['VU:Default']['stepStart']      + " " +
                              config['VU:Default']['colorSpeed']     + " " +
                              config['VU:Default']['subColorSpeed']  + " " +
                              config['VU:Default']['decay']          + " " +
                              config['VU:Default']['reset'])
        
    if select == 'Glow VU':
        taskManager.startTask("LED", "RGB", "python3 /opt/boobot/apps/System/components/virtual/leds/glowVU.py " +
                              ip    + " " +
                              port  + " " +
                              config['GlowVU:Default']['stepStart']      + " " + #  0
                              config['GlowVU:Default']['colorSpeed']     + " " + #  4
                              config['GlowVU:Default']['subColorSpeed']  + " " + # 50
                              config['GlowVU:Default']['decay']          + " " + # .1
                              config['GlowVU:Default']['reset'])                 # 4000
    
    if select == 'Spectrum':
        taskManager.startTask("LED", "RGB", "python3 /opt/boobot/apps/System/components/virtual/leds/spectrum.py " +
                              ip    + " " +
                              port  + " " +
                              config['Spectrum:Default']['stepStart']      + " " +
                              config['Spectrum:Default']['colorSpeed']     + " " +
                              config['Spectrum:Default']['subColor']       + " " +
                              config['Spectrum:Default']['subColorSpeed']  + " " +
                              config['Spectrum:Default']['decay']          + " " +
                              config['Spectrum:Default']['reset'])
        
    if select == '3 Point VU':
        taskManager.startTask("LED", "RGB", "python3 /opt/boobot/apps/System/components/virtual/leds/3PointVU.py " +
                              ip    + " " +
                              port  + " " +
                              config['3PointVU:Default']['stepStart']      + " " +
                              config['3PointVU:Default']['colorSpeed']     + " " +
                              config['3PointVU:Default']['subColor']       + " " +
                              config['3PointVU:Default']['subColorSpeed']  + " " +
                              config['3PointVU:Default']['decay'])

        
    if select == 'Back':
        pass
    return


def createConfig(configurationDirectory, configurationFile, templateFile):
    createFolder    = "mkdir -p " + configurationDirectory
    copyTemplate    = "cp " + templateFile + " " + configurationFile

    os.system(createFolder)

    if not os.path.isfile(os.path.expanduser(configurationFile)):
        os.system(copyTemplate)


def saveConfig(configuration, fileName):
    with open(fileName, 'w') as configfile:
        configuration.write(configfile)
    return


def loadConfig(configuration, fileName):
    configuration.read(os.path.expanduser(fileName))
    return


def getIP():
    return os.popen("hostname -I").read().split()[0]


def main():
    configDirectory = "~/.boobot/RGB"
    configFile      = "~/.boobot/RGB/rgb.config"
    templateFile    = "/opt/boobot/apps/RGB/configuration/rgb.config"
    
    createConfig(configDirectory, configFile, templateFile)
    menu = Menu('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', 12)
    time.sleep(.5)
    mainMenu(menu, configFile)

    
if __name__ == "__main__":
    main()
