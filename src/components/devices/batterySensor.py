import time
import board
import busio
import adafruit_ina219


class BatterySensor:
    def __init__(self):
        self.i2c          = busio.I2C(board.SCL, board.SDA)
        self.sensor       = adafruit_ina219.INA219(self.i2c)
        self.samples      = 10
        self.delay        = .01
        self.voltage      = 0 
        self.shuntVoltage = 0
        self.current      = 0
        

    def update(self):
        sumBusVoltage   = 0
        sumShuntVoltage = 0
        sumCurrent      = 0
    
        for i in range(self.samples):
            time.sleep(self.delay)
            shuntVoltage = self.sensor.shunt_voltage
            sumBusVoltage   += self.sensor.bus_voltage
            sumShuntVoltage += shuntVoltage / 1000
            sumCurrent      += shuntVoltage * 10000000
            
        self.voltage      = sumBusVoltage   / self.samples # V
        self.shuntVoltage = sumShuntVoltage / self.samples # mV
        self.current      = sumCurrent      / self.samples # mA
        

    def charging(self):
        return True if self.current > 1000 else False

    
    def getVoltage(self):
        return self.voltage

    
    def getShuntVoltage(self):
        return self.shuntVoltage

    
    def getCurrent(self):
        return self.current

    
    def getCharge(self):
        if   self.voltage > 8.3:
            return 100
        elif self.voltage > 8.22:
            return 95
        elif self.voltage > 8.16:
            return 90
        elif self.voltage > 8.05:
            return 85
        elif self.voltage > 7.97:
            return 80
        elif self.voltage > 7.91:
            return 75
        elif self.voltage > 7.83:
            return 70
        elif self.voltage > 7.75:
            return 65
        elif self.voltage > 7.71:
            return 60
        elif self.voltage > 7.67:
            return 55
        elif self.voltage > 7.63:
            return 50
        elif self.voltage > 7.59:
            return 45
        elif self.voltage > 7.57:
            return 40
        elif self.voltage > 7.53:
            return 35
        elif self.voltage > 7.49:
            return 30
        elif self.voltage > 7.45:
            return 25
        elif self.voltage > 7.41:
            return 20
        elif self.voltage > 7.37:
            return 15
        elif self.voltage > 7.22:
            return 10
        elif self.voltage > 6.55:
            return  5
        else:
            return  0
