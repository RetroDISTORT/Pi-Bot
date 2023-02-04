import json
import sys
import logging

#sys.path.insert(1, '/opt/boobot/src/components/server')
sys.path.insert(1, '../../src/components/server')
from serverWebsocket     import ServerWebsocket
from serverSocket        import ServerSocket

sys.path.insert(1, '/opt/boobot/src/components/devices')
from servoSet            import ServoSet
from notificationRing    import NotificationRing
from notificationDisplay import NotificationDisplay

# Server data
IP      = "10.0.0.17" #"localhost"
PORT    = 9000
CONFIRM = True        # Send a response to client to notify if the command has completed

servos  = ServoSet()
ring    = NotificationRing()
display = NotificationDisplay()


def logger(log):
    #print("log:", log)
    pass

def execute(message):
    global CONFIRM
    print(message)
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

    if CONFIRM:
        return('{"confirmation": True}')

def main():
    ws = ServerWebsocket(IP, PORT, execute, logger)
    #socket = ServerSocket(IP, PORT, execute, logger)
    #socket.listen()
    
    
if __name__ == "__main__":
    main()
