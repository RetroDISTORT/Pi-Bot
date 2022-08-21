import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) # CENTER

print(GPIO.input(8))
