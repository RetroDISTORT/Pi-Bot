import time
import socket      # Required for sockets
import select      # Required for sockets


class Socket:
    def __init__(self, ip, port, executeMethod, loggerMethod):
        self.execute    = executeMethod
        self.log        = loggerMethod
        self.headerSize = 10
        self.ip         = ip
        self.port       = port
        self.socket     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(5)
        self.log(f'Listening for connections on {self.ip}:{self.port}')

        
    def send(self, message):
        try:
            message = bytes(f"{len(message):<{self.headerSize}}", 'utf-8')+message
            self.socket.send(message)
        except:
            self.log("Error sending message")
            return False


    def recieveMessage(self, clientSocket):
        try:
            fullMessage = b''
            
            while True:
                _, _, _ = select.select([clientSocket], [], []) #Waits for a socket signal
                message = clientSocket.recv(self.headerSize)
                if len(fullMessage)==0:
                    messageLength = int(message[:self.headerSize])
                    newMessage = False

                fullMessage += message

                if len(fullMessage)-self.headerSize == messageLength:
                    return fullMessage[self.headerSize:]

        except:
            self.log('Error getting message. Check header size')
            EXIT_SIG = 0
            return False


    def listen(self):
        EXIT_SIG=True
        
        while EXIT_SIG:
            clientSocket, address = self.socket.accept()
            self.log(f"Connection from {address} has been established.")
            
            while EXIT_SIG:
                message = self.recieveMessage(clientSocket)
                if message==False:
                    self.log("Client Disconnected")
                    break
                else:
                    self.execute(message)
