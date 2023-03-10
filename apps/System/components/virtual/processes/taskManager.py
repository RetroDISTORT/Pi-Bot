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

    
    def killPID(self, target):
        try:
            os.kill(int(target), SIGKILL)
        except:
            return 1
        return 0

    
    def killType(self, target):
        errors = 0
        for process in self.listType(target):
            errors += self.killPID(process[0])
        return errors

    
    def killApplication(self, target):
        errors = 0
        for process in self.listApplication(target):
            errors += self.killPID(process[0])
        return errors


    def startTask(self, taskType, taskApplication, taskCommand):
        command = "bash -c \"exec -a PiBot:" + taskType + ":" + taskApplication + " " + taskCommand + " & \" "
        os.system(command)
        return

                    
    def listAll(self):
        processList = []
        processes = re.findall(".*PiBot.*\n", os.popen("ps aux").read())
        
        for process in processes:
            process      = process.split()
            pid          = process[1]
            cpu          = process[2]
            startTime    = process[8]
            processType  = process[10].split(":")[1]
            application  = process[10].split(":")[-1]
            processList.append([pid, cpu, startTime, processType, application])
    
        return processList
