import time
import board
import signal      # Required for handler
import select      # Used for timeout
import socket
import pickle
import neopixel
import digitalio
from threading import Thread

HEADERSIZE      = 10
IP              = "127.0.0.1" #socket.gethostname()
PORT            = 1235
TIMEOUT_SECONDS = 10
EXIT_SIG        = 1

def handler(signum, frame):
    global EXIT_SIG
    EXIT_SIG = 0
    
    print("Sending end signal to server...", flush=True)
    exit()      
        
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

    return neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER)

def createServerSocket(IP, PORT):    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen(5)
    print(f'Listening for connections on {IP}:{PORT}...')
    return server_socket

def sendMessage(socket, obj):
    try:
        msg = pickle.dumps(obj)
        msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+msg
        #print(msg)
        socket.send(msg)
    except:
        print("Error sending message!")
        return False

def recieveMessage(socket):
    try:
        full_msg = b''
    
        while True:
            msg = socket.recv(16)
            
            if len(full_msg)==0:
                msglen = int(msg[:HEADERSIZE])
                new_msg = False

            full_msg += msg

            if len(full_msg)-HEADERSIZE == msglen:
                return full_msg[HEADERSIZE:]
    except:
        print("Error getting message!")
        return False
        
def serverManager(socket, pixels):

    while EXIT_SIG:
        client_socket, address = socket.accept()
        print(f"Connection from {address} has been established.")

        while EXIT_SIG:
            msg = recieveMessage(client_socket)
            if msg==False:
                print("Client Disconnected")
                break
            else:
                colors = pickle.loads(msg)
                try:
                    setPixels(pixels, colors)
                    sendMessage(client_socket, "Ready")
                except:
                    print("Bad Message: ", end = "")
                    print(colors)
                    sendMessage(client_socket, "Bad Message")
                

def main():
    pixels = setupPixels()
    signal.signal(signal.SIGINT, handler)

    server_socket = createServerSocket(IP,PORT)
    serverManager(server_socket, pixels)

    #pixels.fill((0, 0, 0));
    #pixels.show()

if __name__ == "__main__":
    main()
