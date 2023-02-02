import websockets
import asyncio


servoTest1 = ('{'
             '"device":           "Servo",'
             '"command":          "setAllServos",'
             '"leftServoAngle":   100,'
             '"rightServoAngle":  100,'
             '"cameraServoAngle":  0'
             '}')

servoTest2 = ('{'
             '"device":  "Servo",'
             '"command": "setServo",'
             '"servo":   9,'
             '"angle":   10'
             '}')

servoTest3 = ('{'
             '"device":  "Servo",'
             '"command": "Disable"'
             '}')

displayTest1 = ('{'
             '"device":  "Display",'
             '"command": "showMessage",'
             '"message": "Short message"'
             '}')

displayTest2 = ('{'
             '"device":  "Display",'
             '"command": "showMessage",'
             '"message": "Longer message that requires scroll to display"'
             '}')

displayTest3 = ('{'
             '"device":  "Display",'
             '"command": "clear"'
             '}')

pixelTest1 = ('{'
              '"device":  "LED",'
              '"command": "fill",'
              '"color":   [255,255,255]'
              '}'
              )

pixelTest2 = ('{'
              '"device":  "LED",'
              '"command": "setBrightness",'
              '"brightness": 0.08'
              '}'
              )


pixelTest3 = ('{'
              '"device":  "LED",'
              '"command": "clear"'
              '}'
              )

pixelTest4 = ('{'
              '"device":  "LED",'
              '"command": "setPixels",'
              '"colors":  [[255,0,0], [255,50,0], [255,150,0], [255,255,0], [150,255,0], [50,255,0], [50,255,0], [0,255,50], [0,255,150], [0,255,255], [0,150,255], [0,50,255], [0,0,255], [150,0,255], [255,0,255], [255,0,8]]'
              '}'
              )

serverTest1 = ('{'
              '"device":  "Server",'
              '"command": "confirmation",'
              '"enable":  true'
              '}'
              )

userTest = ('{'
             '"device":  "Display",'
             '"command": "showMessage",'
             '"message": "Client Connected!"'
             '}')

async def listen():
    url = "ws://10.0.0.17:9000"

    async with websockets.connect(url) as ws:
        await ws.send(serverTest1)

        #while True:
        msg = await ws.recv()
        print(msg)
        return


asyncio.get_event_loop().run_until_complete(listen())
