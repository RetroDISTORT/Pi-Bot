import time
from adafruit_servokit import ServoKit

# Set channels to the number of servo channels on your kit.
# 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
kit = ServoKit(channels=16, address = 0x41))

# Wheels are on 0 and 3. Camera is on 9 
kit.servo[9].angle = 100 # Motors stop at 100
