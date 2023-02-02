import time
import board
import neopixel   # Used for neopixels
import digitalio
from digitalio import DigitalInOut, Direction, Pull

class NotificationRing:
    def __init__(self):
        self.pixelCount           = 16
        self.pixelOrder           = neopixel.GRB
        self.pixelBrightness      = 0.1
        self.enablePin            = digitalio.DigitalInOut(board.D15)
        self.dataPin              = board.D12
        self.enablePin.direction  = digitalio.Direction.OUTPUT
        self.enablePin.value      = True
        self.pixels               = neopixel.NeoPixel(self.dataPin, self.pixelCount, brightness = self.pixelBrightness, auto_write=False, pixel_order=self.pixelOrder)

        
    def setBrightness(self, brightness):
        self.pixelBrightness      = brightness
        self.pixels               = neopixel.NeoPixel(self.dataPin, self.pixelCount, brightness=self.pixelBrightness, auto_write=False, pixel_order=self.pixelOrder)
        self.pixels.show()


    def setPixels(self, colors):
        for i in range(len(colors[:self.pixelCount])):
            self.pixels[i]=tuple(colors[i])
        self.pixels.show()


    def fill(self, color):
        self.pixels.fill(tuple(color))
        self.pixels.show()

    def clear(self):
        self.pixels.fill([0,0,0])
        self.pixels.show()

