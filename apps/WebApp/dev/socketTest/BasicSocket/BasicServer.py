import time
import board
import signal      # Required for handler
import select      # Used for timeout
import socket
import pickle


HEADERSIZE      = 10
IP              = "" #socket.gethostname()
PORT            = 1235
EXIT_SIG        = 1

def handler(signum, frame):
    global EXIT_SIG
    EXIT_SIG = 0
    
    print("Sending end signal to server...", flush=True)
    exit()      
        

def getIP():
    global IP;
    if (IP == ""):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
        
    
def createServerSocket(IP, PORT):    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        
def serverManager(socket):

    while EXIT_SIG:
        client_socket, address = socket.accept()
        print(f"Connection from {address} has been established.")

        while EXIT_SIG:
            msg = recieveMessage(client_socket)
            if msg==False:
                print("Client Disconnected")
                break
            else:
                decodedMessage = pickle.loads(msg)
                try:
                    print(decodedMessage)
                    sendMessage(client_socket, "Ready")
                except:
                    print("Bad Message: ", end = "")
                    sendMessage(client_socket, "Bad Message")
                

def main():
    signal.signal(signal.SIGINT, handler)
    getIP();
    server_socket = createServerSocket(IP,PORT)
    
    serverManager(server_socket)


if __name__ == "__main__":
    main()
