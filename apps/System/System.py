import os               # Required for running command line functions
import re               # Required for regex
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
        select = menu.displayMenu(['Tasks', 'Server', 'About', 'Exit'])
        
        if select == 'Tasks':
            taskPanel(menu, taskManager)
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
                taskManager.killPID(taskPID)
                menu.displayMessage(" PID:" + taskPID + " killed")


def serverMenu(menu, taskManager):
    while True:
        Server      = taskManager.listType('Server')
        menuOptions = ['Start Server', 'Exit'] if len(Server) == 0 else ['Server info', 'Kill Server', 'Exit']
        select = menu.displayMenu(menuOptions)
    
        if select == 'Start Server':
            if menu.displayToggle("Enable:", ['True', 'False'], 0) == 'True':
                taskManager.startTask('Server', 'System', "sudo python3 /opt/boobot/apps/System/programs/Server.py")

        if select == 'Kill Server':
            taskManager.killType('Server')

        if select == 'Server info':
            menu.displayLargeMessage(["   Server Connection", "IP: "+getIP(), "Port(WS): 9000", "Port(S): 9001", "", "      [Click to Exit]"])
                
        if select == 'Exit':
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
    menu = Menu('/opt/boobot/apps/System/fonts/ratchet-clank-psp.ttf', 12)
    time.sleep(.5)
    mainMenu(menu)
    
    


if __name__ == "__main__":
    main()
