import time
import errno
import socket
import signal      # Required for handler
import pickle      # Required to convert objects to raw data
import select
from math import ceil as ceil

DELAY           = 1/1        # .0167 is about 60fps
CONFIRMATION    = True         # This helps prevent overloading the server
HEADERSIZE      = 10
IP              = "" #socket.gethostname() #"127.0.0.1"
PORT            = 1235
EXIT_SIG        = 1


def handler(signum, frame):
    global EXIT_SIG
    EXIT_SIG = 0
    
    print("Sending end signal to server...", flush=True)


def getIP():
    global IP;
    if (IP == ""):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    

def createClientSocket(IP, PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    client_socket.setblocking(False)
    
    return client_socket

def sendMessage(socket, obj):    
    msg = pickle.dumps(obj)
    msg = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+msg
    #print(msg)
    socket.send(msg)

def ConfirmationResponse(socket):
    if CONFIRMATION == False:
        return
    
    msg = recieveMessage(socket)
    if msg==False:
        print("Bad Server Response\n Closing Program.")
        exit()

    
def recieveMessage(socket):
    while EXIT_SIG:
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

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

                # We just did not receive anything
                continue

        except Exception as e:
            print('Reading error: '.format(str(e)))
            exit()
    
            
def Client(socket):
    global EXIT_SIG
    
    while EXIT_SIG:
        time.sleep(DELAY)
        sendMessage(socket, "Message from client!!!")
        msg = recieveMessage(socket)
        decodedMessage = pickle.loads(msg)
        print(decodedMessage)
        #ConfirmationResponse(socket)
        

        
def main():
    signal.signal(signal.SIGINT, handler)
    getIP();
    client_socket  = createClientSocket(IP, PORT)
    
    Client(client_socket) 

    
if __name__ == "__main__":
    main()
