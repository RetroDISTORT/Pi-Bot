# Importing the relevant libraries
import websockets
import asyncio
import json

# Server data
IP   = "10.0.0.14"#"localhost"
PORT = 9000

print("Server listening on Port " + str(PORT))

async def echo(websocket, path):
    print("A client just connected")
    try:
        async for rawMessage in websocket:
            print("Received message from client: " + rawMessage)
            message = json.loads(rawMessage)
            
            if "message" in message:
                await websocket.send(">> " + message["message"])
                
            if "joystick_x" in message:
                pass;
            
            if "joystick_y" in message:
                pass;

            if "slider_y" in message:
                pass;

            if "led" in message:
                pass;

            if "display" in message:
                pass;

            if "update" in message:
                #send compass update
                pass;
            
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")

start_server = websockets.serve(echo, IP, PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
