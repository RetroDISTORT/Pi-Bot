import time
import board
import neopixel   # Used for neopixels
import digitalio

class LightRing:
    def __init__(self):
        self.pixelCount           = 16
        self.pixelOrder           = neopixel.RGB
        self.pixelBrightness      = .2
        self.enablePin            = digitalio.DigitalInOut(board.D15)
        self.dataPin              = board.D12
        self.enablePin.direction  = digitalio.Direction.OUTPUT
        self.enablePin.value      = True
        self.pixels               = neopixel.NeoPixel(self.dataPin, self.pixelCount, brightness=pixelBrightness, auto_write=False, pixel_order=pixelOrder)

        
    def brightness(self, brightness):
        self.pixelBrightness      = brightness
        self.pixels               = neopixel.NeoPixel(self.dataPin, self.pixelCount, brightness=pixelBrightness, auto_write=False, pixel_order=pixelOrder)


    def setPixels(pixels, colors):
        for i in range(len(colors[:self.pixelCount])):
            pixels[i]=colors[i]
        pixels.show()


    def fillPixels(self, color):
        pixels.fill(color)
        pixels.show()

