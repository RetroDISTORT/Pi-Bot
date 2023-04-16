import time             # Required for delays
import board            # Required for I2C bus
import busio            # Required for I2C bus
import digitalio        # Required for I2C bus


class Menu:
    def __init__(self, wait=.1):
        self.wait          = wait
        self.live          = True
        self.data          = []
        self.micDataLock   = Lock()
        self.newDataEvent  = Event()
        self.newDataEvent.clear()
        self.captureThread = Thread(target=self.capture)
        self.captureThread.start()


    def capture(self):
        lastActive = []
        active     = []
        GPIO.setup(7,  GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
        GPIO.setup(8,  GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # CENTER
        
        while self.live:
            time.sleep(self.wait)
            active = [GPIO.input(8) == 0, GPIO.input(25) == 0, GPIO.input(7)  == 0]
            if active != lastActive:
                lastActive = [i for i in active]
                with self.dataLock:
                    self.data = np.array(self.capturedData).flatten()
                    self.capturedData = []
                    self.newMicDataEvent.set()
        

    def input(self):
        self.prevOptions = None
        
    def displayMenu(self, options, returnOptions=False):
        self.drawMenu(options)
        
