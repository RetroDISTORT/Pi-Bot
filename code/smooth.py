import time
import keyboard
from adafruit_servokit import ServoKit

from sshkeyboard import listen_keyboard
import neopixel
import digitalio
import board
from rainbowio import colorwheel

########### PID ###########
# PID control system
# constants.
###########################
P = 1                     # Proportional
I = 2                     # Integral
D = 3                     # Derivative
########### ENV ###########
# Enviornmental varsiables
# These simulate an
# external forces
###########################
acceleration = .1         # only edit this
speed = 0                 # current speed
start = 0                 # start position
end = 0                   # ending position
position = 0              # current position
time = time.time() * 1000 # current time in milliseconds

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
#kit = ServoKit(channels=16, address = 0x41)

# Wheels are on 0 and 3. Camera is on 9 
#kit.servo[9].angle = 100 # Motors stop at 100


# enable Neopixels                                                                                                          
led = digitalio.DigitalInOut(board.D15)
led.direction = digitalio.Direction.OUTPUT
led.value = True

pixel_pin  = board.D12
num_pixels = 16
pixels = neopixel.NeoPixel(pixel_pin, num_pixels)
ORDER = neopixel.GRB


pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.05, auto_write=True, pixel_order=ORDER)

red = 200
green = 200
blue = 200

def press(key):
    global red
    global blue
    global green
    if(key=='r'):
        red = 255
        print("r")
    if(key=='g'):
        green = 200
        print("g")
    if(key=='b'):
        blue = 200
        print("b")
    pixels.fill((red, green, blue));

def release(key):
    global red
    global green
    global blue
    if(key=='r'):
        print("R")
        red = 0
    if(key=='g'):
        print("G")
        green = 0
    if(key=='b'):
        print("")
        blue = 0
    pixels.fill((red, green, blue));

listen_keyboard(
    on_press=press,
    on_release=release,
    )
