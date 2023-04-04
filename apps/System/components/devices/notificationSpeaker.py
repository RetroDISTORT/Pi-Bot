import digitalio
import board

class NotificationSpeaker:
    def __init__(self):
        self.enablePin            = digitalio.DigitalInOut(board.D27)
        self.enablePin.direction  = digitalio.Direction.OUTPUT
        

    def status(self):
        return self.enablePin.value

    
    def enable(self):
        self.enablePin.value = True

        
    def disable(self):
        self.enablePin.value = False
        
