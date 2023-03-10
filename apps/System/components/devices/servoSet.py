from adafruit_servokit import ServoKit

class ServoSet:
    def __init__(self):
        self.leftServoPin   = 0
        self.rightServoPin  = 3
        self.cameraServoPin = 9
        self.servoSet       = ServoKit(channels=16, address = 0x41)

                               
    def disableServos(self):
        for servo in [self.leftServoPin, self.rightServoPin, self.cameraServoPin]:
            self.servoSet.servo[servo].angle = None

            
    def servoAngle(self, pin, value):
        self.servoSet.servo[pin].angle = value


    def getServoAngle(self, pin):
        return self.servoSet.servo[pin].angle

