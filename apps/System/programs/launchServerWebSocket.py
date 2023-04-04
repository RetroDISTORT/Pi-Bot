import json
import sys
import logging

sys.path.insert(1, '/opt/boobot/apps/System/components/virtual/server')
from serverWebsocket     import ServerWebsocket

sys.path.insert(1, '/opt/boobot/apps/System/components/devices')
from servoSet            import ServoSet
from notificationRing    import NotificationRing
from notificationDisplay import NotificationDisplay
from batterySensor       import BatterySensor

# Server data
IP             = "" #"localhost"
CONFIRM        = True        # Send a response to client to notify if the command has completed
WEBSOCKET_PORT = 9000

servos        = ServoSet()
ring          = NotificationRing()
display       = NotificationDisplay()
battery       = BatterySensor()

servos.servoAngle(0, None)
servos.servoAngle(3, None)
servos.servoAngle(9, None)


def logger(log):
    #print("log:", log)
    pass

def execute(message):
    global CONFIRM

    try:
        input = json.loads(message)
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        return

    if input["device"] == "Server":
        if input["command"] == "confirmation":
            CONFIRM = input["enable"]
    
    elif input["device"] == "Servo":
        if input["command"] == "setAllServos":
            servos.servoAngle(0, input["leftServoAngle"])
            servos.servoAngle(3, input["rightServoAngle"])
            servos.servoAngle(9, input["cameraServoAngle"])

        elif input["command"] == "setServo":
            servos.servoAngle(input["servo"], input["angle"])

        elif input["command"] == "getServo":
            return str(servos.getServoAngle(input["servo"]))
            
        elif input["command"] == "Disable":
            servos.disableServos()

    elif input["device"] == "Display":
        if input["command"] == "showMessage":
            display.showMessage(input["message"])

        elif input["command"] == "clear":
            display.clear()

    elif input["device"] == "LED":
        if input["command"] == "setBrightness":
            ring.setBrightness(input["brightness"])

        elif input["command"] == "clear":
            ring.clear()
            
        elif input["command"] == "fill":
            ring.fill(input["color"])

        elif input["command"] == "setPixels":
            ring.setPixels(input["colors"])

    elif input["device"] == "Battery":
        if input["command"] == "voltage":
            battery.update()
            return(str(battery.getVoltage()))

        if input["command"] == "current":
            battery.update()
            return(str(battery.getCurrent()))

        if input["command"] == "shunt":
            battery.update()
            return(str(battery.getShuntVoltage()))

        if input["command"] == "charge":
            battery.update()
            return(str(battery.getCharge()))

        if input["command"] == "charging":
            battery.update()
            return(str(battery.charging()))

    if CONFIRM:
        return('{"confirmation": True}')


def socketManager():
    socket = ServerSocket(IP, SOCKET_PORT, execute, logger)
    socket.listen()

    
def main():
    ws = ServerWebsocket(IP , WEBSOCKET_PORT, execute, logger)

    
if __name__ == "__main__":
    main()
