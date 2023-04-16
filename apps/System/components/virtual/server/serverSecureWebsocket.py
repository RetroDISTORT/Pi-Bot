import asyncio    # Used for websockets
import websockets # Used for websockets
import socket     # Required for sockets
#import ssl

class ServerWebsocket:
    def __init__(self, ip, port, executeMethod, loggerMethod):
        self.execute = executeMethod
        self.log     = loggerMethod
        self.ip      = self.getIP(ip)
        self.port    = port
        ssl_context  = ssl.SSLContext()
        ssl_context.load_cert_chain("/home/pi/Documents/certification/ws/ws.crt", "/home/pi/Documents/certification/ws/ws.key")
        startServer  = websockets.serve(self.listen, self.ip, self.port, reuse_port=True)#, ssl=ssl_context)
        
        self.log("Server listening on " + str(self.ip)+ ":" + str(self.port))
        asyncio.get_event_loop().run_until_complete(startServer)
        asyncio.get_event_loop().run_forever()
        

    def getIP(self, IP):
        if (IP == ""):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            IP = s.getsockname()[0]
        return IP
        

    async def send(self, websocket, message):
        try:
            await websocket.send(message)
        except:
            self.log("Error sending message")
            return False
            
    async def listen(self, websocket, path):
        self.log("Client " + str(websocket.remote_address) + " connected")
        try:
            async for message in websocket: 
                self.log("Message from client " + str(websocket.remote_address) + ":" + message)
                serverMessage = self.execute(message)
                if serverMessage:
                    self.log("Message to client " + str(websocket.remote_address) + ":" + serverMessage)
                    await self.send(websocket, serverMessage)
                
            
        except websockets.exceptions.ConnectionClosed as e:
            self.log("Client Exception " + str(websocket.remote_address) + ": " + str(e))

        self.log("Client " + str(websocket.remote_address) + " disconnected")
