import time
import json       # Used for sockets and websockets
import board
import signal     # Required for handler
import select     # Used for timeout sockets
import socket
import pickle
import asyncio    # Used for websockets
import neopixel   # Used for neopixels
import digitalio  
import websockets # Used for websockets

from threading import Thread

HEADERSIZE      = 10
IP              = "" #socket.gethostname() #"127.0.0.1"
PORT            = 9000
TIMEOUT_SECONDS = 10
CONFIRMATION    = True
EXIT_SIG        = 1
BRIGHTNESS      = .2 #Default brightness
LOGMODE         = False

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
    
def setPixels(pixels, colors):
    for i in range(len(colors[:16])):
        pixels[i]=colors[i]
    pixels.show()

def setupPixels():
    # enable Neopixels                                                                                                          
    led = digitalio.DigitalInOut(board.D15)
    led.direction = digitalio.Direction.OUTPUT
    led.value = True

    pixel_pin  = board.D12
    num_pixels = 16
    ORDER = neopixel.RGB

    return neopixel.NeoPixel(pixel_pin, num_pixels, brightness=BRIGHTNESS, auto_write=False, pixel_order=ORDER)

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

    
def serverManager(socket, pixels):
    pixels.fill((0, 0, 0));
    pixels.show()
    
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
                print(msg)
                runCommand(client_socket, command, pixels)

                
def runCommand(socket, command, pixels):
    global CONFIRMATION
    if type(command[0]) is tuple:
        try:
            setPixels(pixels, command)
        except:
            logger("Bad Message: " + str(command))
            
    elif type(command[0]) is str:
        if command[0] == "Brightness":
            try:
                pixels.brightness = command[1]
            except:
                logger("Bad Message: " + str(command))
                
        elif command[0] == "Confirmation":
            if type(command[1]) == bool:
                CONFIRMATION = command[1]
            else:
                print("Bad Message: " + str(command))
            
    if CONFIRMATION:
        sendMessage(socket, "READY")
        #sendConfirmation(socket)


def main():
    pixels = setupPixels()
    signal.signal(signal.SIGINT, handler)
    server_socket = createServerSocket(IP,PORT)
    serverManager(server_socket, pixels)

if __name__ == "__main__":
    main()
