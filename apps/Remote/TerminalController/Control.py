import time
import board
import signal      # Required for handler
import select      # Used for timeout
import socket
import pickle
import digitalio
import time
from adafruit_servokit import ServoKit
from threading import Thread

HEADERSIZE      = 10
IP              = ""
PORT            = 1236
TIMEOUT_SECONDS = 10
CONFIRMATION    = True
EXIT_SIG        = 1
LOGMODE         = True

# REQUIRED FOR MOTOR CONTORL
MOTOR1_SPEED        = 100
MOTOR1_ACCELERATION = 2
MOTOR1_TOP_SPEED    = 180
MOTOR1_BREAKING     = 10

MOTOR2_SPEED        = 100
MOTOR2_ACCELERATION = 2
MOTOR2_TOP_SPEED    = 0
MOTOR2_BREAKING     = 10

CAMERA_ANGLE            = 45
CAMERA_SPEED            = 0
CAMERA_ACCELERATION     = .01
CAMERA_MAX_ACCELERATION = .1
CAMERA_MIN_ANGLE        = 0
CAMERA_MAX_ANGLE        = 180

def logger(log):
    if LOGMODE:
        print(log)

def handler(signum, frame):
    global EXIT_SIG
    EXIT_SIG = 0
    logger("Sending end signal to server...")
    exit()      

    
def getIP(IP):
    if (IP == ""):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
        return IP
    

def createServerSocket(IP, PORT):
    IP = getIP(IP)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen(5)
    logger(f'Listening for connections on {IP}:{PORT}...')
    return server_socket

def sendMessage(socket, obj):
    try:
        msg = pickle.dumps(obj)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+msg
        socket.send(msg)
    except:
        logger("Error sending message!")
        return False


def sendConfirmation(socket):
    try:
        msg = bytes(f"{0:<{HEADERSIZE}}", 'utf-8')
        socket.send(msg)
    except:
        logger("Error sending message!")
        return False

    
def recieveMessage(socket):
    try:
        full_msg = b''
    
        while True:
            _, _, _ = select.select([socket], [], []) #Waits for a socket signal
            msg = socket.recv(16)
            if len(full_msg)==0:
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            full_msg += msg

            if len(full_msg)-HEADERSIZE == msglen:
                return full_msg[HEADERSIZE:]
    except:
        logger("Error getting message!")
        return False

    
def serverManager(socket, kit):
    while EXIT_SIG:
        client_socket, address = socket.accept()
        logger(f"Connection from {address} has been established.")

        while EXIT_SIG:
            msg = recieveMessage(client_socket)
            if msg==False:
                logger("Client Disconnected")
                break
            else:
                command = pickle.loads(msg)
                runCommand(client_socket, command, kit)


def motor(keysPressed, kit):
    global MOTOR1_SPEED
    global MOTOR2_SPEED
    
    if 'a' in keysPressed or 'w' in keysPressed:
        MOTOR1_SPEED += MOTOR1_ACCELERATION
        MOTOR1_SPEED  = MOTOR1_SPEED if MOTOR1_SPEED < MOTOR1_TOP_SPEED else MOTOR1_TOP_SPEED
    else:
        MOTOR1_SPEED -= MOTOR1_BREAKING
        MOTOR1_SPEED  = MOTOR1_SPEED if MOTOR1_SPEED > 100 else 100

    if 'd' in keysPressed or 'w' in keysPressed:
        MOTOR2_SPEED -= MOTOR2_ACCELERATION
        MOTOR2_SPEED  = MOTOR2_SPEED if MOTOR2_SPEED > MOTOR2_TOP_SPEED else MOTOR2_TOP_SPEED
    else:
        MOTOR2_SPEED += MOTOR2_BREAKING
        MOTOR2_SPEED  = MOTOR2_SPEED if MOTOR2_SPEED < 100 else 100

    # Wheels are on 0 and 3. Camera is on 9 
    kit.servo[0].angle = MOTOR1_SPEED # Motors stop at 100
    kit.servo[3].angle = MOTOR2_SPEED # Motors stop at 100
        
                
def runCommand(socket, command, kit):
    global CONFIRMATION
    motor(command, kit)
            
    if CONFIRMATION:
        sendMessage(socket, "READY")
        #sendConfirmation(socket)


def main():
    kit = ServoKit(channels=16, address = 0x41)
    kit.servo[0].angle = 100 # Motors stop at 100
    kit.servo[3].angle = 100 # Motors stop at 100
    
    signal.signal(signal.SIGINT, handler)
    server_socket = createServerSocket(IP,PORT)
    serverManager(server_socket, kit)

if __name__ == "__main__":
    main()
