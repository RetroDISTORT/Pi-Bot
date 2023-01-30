import asyncio    # Used for websockets
import websockets # Used for websockets

class Websocket:
    def __init__(self, ip, port, executeMethod, loggerMethod):
        self.execute = executeMethod
        self.log     = loggerMethod
        self.ip      = ip
        self.port    = port
        startServer = websockets.serve(self.listen, IP, PORT)
        
        self.log("Server listening on " + str(IP)+ ":" + str(PORT))
        asyncio.get_event_loop().run_until_complete(startServer)
        asyncio.get_event_loop().run_forever()
        


    async def send(self, meessage):
        try:
            await websocket.send(message)
        except:
            self.log("Error sending message")
            return False
            
    async def listen(websocket, path):
        self.log("Client connected")
        try:
            async for message in websocket:
                self.log("Received message from client: " + message)
                self.execute(message)
            
        except websockets.exceptions.ConnectionClosed as e:
            self.log("Client disconnected")
