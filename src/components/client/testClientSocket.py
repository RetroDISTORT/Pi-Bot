import sys
sys.path.insert(1, './')
from clientSocket import ClientSocket

IP   = "10.0.0.17"
PORT = 9000 

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

socket = ClientSocket(IP, PORT)
socket.send(serverTest1)
print(socket.recieve())
