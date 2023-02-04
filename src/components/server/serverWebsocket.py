import asyncio    # Used for websockets
import websockets # Used for websockets

class ServerWebsocket:
    def __init__(self, ip, port, executeMethod, loggerMethod):
        self.execute = executeMethod
        self.log     = loggerMethod
        self.ip      = ip
        self.port    = port
        startServer  = websockets.serve(self.listen, self.ip, self.port, reuse_port=True )
        
        self.log("Server listening on " + str(self.ip)+ ":" + str(self.port))
        asyncio.get_event_loop().run_until_complete(startServer)
        asyncio.get_event_loop().run_forever()
        


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
