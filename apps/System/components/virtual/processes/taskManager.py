import os               # Required for running command line functions
import time             # Required for delays
import sys              # Required for loading special modules
import re               # Required for regex

from signal import SIGKILL

# Constants
PID  = 0
CPU  = 1
TIME = 2
TYPE = 3
APP  = 4

class TaskManager:
    def __init__(self):
        return

    
    def listType(self, target):
        processList = []
        for process in self.listAll():
            if process[TYPE] == target:
                processList.append(process)
        return processList

    
    def listApplication(self, target):
        processList = []
        for process in self.listAll():
            if process[APP] == target:
                processList.append(process)
        return processList

    
    def killPID(self, target, sudo=False):
        if sudo:
            command = "sudo kill -9 " + target
            os.system(command)
            pass
        else:
            try:
                os.kill(int(target), SIGKILL)
            except:
                return 1
        return 0

    
    def killType(self, target, sudo=False):
        errors = 0
        for process in self.listType(target):
            errors += self.killPID(process[0], sudo)
        return errors

    
    def killApplication(self, target, sudo=False):
        errors = 0
        for process in self.listApplication(target, sudo):
            errors += self.killPID(process[0])
        return errors


    def startTask(self, taskType, taskApplication, taskCommand, sudo=False):
        command = "bash -c \"exec -a PiBot:" + taskType + ":" + taskApplication + " " + taskCommand + " & \" "
        
        if sudo == True:
            command = "sudo bash -c \"exec -a PiBot:" + taskType + ":" + taskApplication + " " + taskCommand + " & \" "
            
        os.system(command)
        return

                    
    def listAll(self):
        processList = []
        processes = re.findall(".*PiBot.*\n", os.popen("ps aux").read())

        for process in processes:

            processFull  = process
            process      = process.split()
            pid          = process[1]
            cpu          = process[2]
            startTime    = process[8]

            try:
                if len(processes) < 10 or len(processes[10].split) < 3:
                    startIndex  = processFull.index("PiBot:")
                    endIndex    = processFull.find(' ', startIndex)
                    process[10] = processFull[startIndex : endIndex]
                    
                    processType  = process[10].split(":")[1]
                    application  = process[10].split(":")[-1]
            
                    processList.append([pid, cpu, startTime, processType, application])
            except:
                pass #Error retrieving getting processType and application
    
        return processList
