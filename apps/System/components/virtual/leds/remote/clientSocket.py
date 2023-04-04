import socket
import select

class ClientSocket:
    def __init__(self, ip, port):
        self.ip           = ip
        self.port         = port
        self.headerSize   = 10
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print(self.ip, self.port)
        self.clientSocket.connect((self.ip, self.port))
        self.clientSocket.setblocking(False)


    def send(self, message):
        try:
            message = bytes(message, 'utf-8')
            message = bytes(f"{len(message):<{self.headerSize}}", 'utf-8')+message
            self.clientSocket.send(message)
        except:
            return False
        


    def recieve(self):
        while True:
            try:
                fullMessage = b''
            
                while True:
                    _, _, _ = select.select([self.clientSocket], [], []) #Waits for a socket signal
                    message = self.clientSocket.recv(16)
                    
                    if len(fullMessage)==0:
                        messageLength = int(message[:self.headerSize])
                        newMessage = False
                        
                    fullMessage += message

                    if len(fullMessage)-self.headerSize == messageLength:
                        return fullMessage[self.headerSize:]

            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    exit()
                
                # We just did not receive anything
                continue

            except Exception as e:
                print('Reading error: '.format(str(e)))
                EXIT_SIG = 0
                exit()
