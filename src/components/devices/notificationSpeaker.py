import digitalio
import board

class NotificationSpeaker:
    def __init__(self):
        self.enablePin            = digitalio.DigitalInOut(board.D27)
        self.enablePin.direction  = digitalio.Direction.OUTPUT
        self.enablePin.value      = True

    def enable(self, state):
        self.enablePin.value = state
        
