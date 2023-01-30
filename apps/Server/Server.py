import json
import sys

sys.path.insert(1, './src/')

from server_websocket import Websocket
from server_socket    import Socket

# Server data
IP   = "10.0.0.17"#"localhost"
PORT = 9000

def logger(log):
    print("log:", log)

def execute(message):
    print("exec:", message)

def main():
    #ws = Websocket(IP, PORT, execute, logger)
    socket = Socket(IP, PORT, execute, logger)
    socket.listen()

if __name__ == "__main__":
    main()
