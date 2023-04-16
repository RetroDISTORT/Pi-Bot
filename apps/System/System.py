import os               # Required for running command line functions
import re               # Required for regex
import sys              # Required for loading special modules
import time             # Required for delays
import socket           # required to get IP
import configparser     # Required for ini files

from signal import SIGKILL

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/display')
from menu         import Menu
from canvas       import Canvas

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/processes')
from taskManager  import TaskManager    

sys.path.insert(1, '/opt/boobot/apps/System/components/devices')
from notificationSpeaker import NotificationSpeaker
from servoSet            import ServoSet
from batterySensor       import BatterySensor


def mainMenu(menu):
    taskManager = TaskManager()
    
    while True:
        select = menu.displayMenu(['Tasks', 'Server', 'WiFi', 'Bluetooth', 'Status', 'Components', 'About', 'Exit'])
        
        if select == 'Tasks':
            taskPanel(menu, taskManager)
        if select == 'Components':
            componentMenu(menu, taskManager)
        if select == 'Status':
            statusMenu(menu)
        if select == 'WiFi':
            wifiMenu(menu)
        if select == 'Bluetooth':
            bluetoothMenu(menu)
        if select == 'Server':        
            serverMenu(menu, taskManager)
        if select == 'Settings':
            settingsMenu(menu)
        if select == 'About':
            menu.displayLargeMessage(["      Pi-Bot System", "--------------------------", "       V 0.23.2.26", " Github: RetroDISTORT", "", "      [Click to Exit]"])
        if select == 'Exit':
            menu.displayOff()
            return


def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = s.getsockname()[0]
            
    return IP

        
def taskPanel(menu, taskManager):
    while True:
        taskList = taskManager.listAll() #runningProcess()
    
        if len(taskList) == 0:
            menu.displayMessage("No Tasks Found")
            return

        if isinstance(taskList[0], list):
            taskNames = [task[0] + " " + task[3] + ":" + task[4] for task in taskList]
        else:
            taskNames = [taskList[0] + " " + taskList[3] + ":" + taskList[4]]
        taskNames.append("return")
    
        selectedTask = menu.displayMenu(taskNames)
        if selectedTask == "return":
            return
        else:
            if menu.displayToggle("End Task:", ['Yes', 'No'], 0) == 'Yes':
                taskPID = selectedTask.split()[0]
                if taskManager.killPID(taskPID) == 0:
                    menu.displayMessage(" PID:" + taskPID + " killed")
                else:
                    menu.displayMessage(" Could not Kill PID: " + taskPID + ". If this is a server, kill from server menu.")


def statusMenu(menu):
    while True:
        while 'select' in menu.getInput(): pass
        menuOptions = ['Battery', 'Back']
        select = menu.displayMenu(menuOptions)
    
        if select == 'Battery':
            battery = BatterySensor()
            graph   = Canvas()
            data    = [0]*50
            
            while(True):
                battery.update()
                data.append(battery.getVoltage())
                data.pop(0)
                graph.addGraph(0,16,128,32,data)
                graph.addText(0,0,"Charging" if not battery.charging else "Not Charging")
                graph.addText(100,50,str(battery.getCharge())+'%')
                #graph.addText(74,20,f'{battery.getVoltage():.3f}V')
                graph.addText(0,20,f'{battery.getVoltage():.3f}V')
                graph.addText(20,50,"[Click to Exit]")
                graph.drawCanvas()
                if 'select' in menu.getInput():
                    break
                
        if select == 'Back':
            return


def bluetoothMenu(menu):
    while True:
        while 'select' in menu.getInput(): pass
        menuOptions = ['Power', 'Connect', 'Devices', 'Advertise', 'Remove', 'Back']
        select = menu.displayMenu(menuOptions)
        if select == 'Back':
            return

def wifiMenu(menu):
    while True:
        while 'select' in menu.getInput(): pass
        menuOptions = ['Power', 'Connect', 'Devices', 'Advertise', 'Remove', 'Back']
        select = menu.displayMenu(menuOptions)
        if select == 'Back':
            return

        
def componentMenu(menu, taskManager):
    while True:    
        menuOptions = ['Speaker', 'Disengage Servos', 'Back']
        select = menu.displayMenu(menuOptions)
    
        if select == 'Speaker':
            speaker = NotificationSpeaker()
            if menu.displayToggle("Enable:", ['True', 'False'], 0) == 'True':
                speaker.enable()
            else:
                speaker.disable()

        if select == 'Disengage Servos':
            servos = ServoSet()
            servos.disableServos()

        if select == 'Back':
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
                taskManager.startTask('WebSocketServer', 'System', "python3 /opt/boobot/apps/System/programs/launchServerWebSocket.py", True)

        if select == 'Start S Server':
            if menu.displayToggle("Enable:", ['True', 'False'], 0) == 'True':
                taskManager.startTask('SocketServer', 'System', "python3 /opt/boobot/apps/System/programs/launchServerSocket.py", True)

        if select == 'Kill S Server':
            taskManager.killType('SocketServer', True)

        if select == 'Kill WS Server':
            taskManager.killType('WebSocketServer', True)

        if select == 'Server info':
            menu.displayLargeMessage(["   Server Connection", "IP: "+getIP(), "Port(WS): 9000", "Port(S): 9001", "", "      [Click to Exit]"])
                
        if select == 'Back':
            return

        

def main():
    menu = Menu('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', 12)
    time.sleep(.5)
    mainMenu(menu)
    
    
if __name__ == "__main__":
    main()
