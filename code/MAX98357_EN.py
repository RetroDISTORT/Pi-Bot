import digitalio
import board

# enable MAX98357                                                                                                        
en_pin = digitalio.DigitalInOut(board.D27) #GPIO27
en_pin.direction = digitalio.Direction.OUTPUT
en_pin.value = True
