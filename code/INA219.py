import time
import board
import busio
import adafruit_ina219


def getAverage(sensor, samples, delay):
    sumBusVoltage   = 0
    sumShuntVoltage = 0
    sumCurrent      = 0
    
    for i in range(samples):
        time.sleep(delay)
        shuntVoltage = sensor.shunt_voltage
        sumBusVoltage   += sensor.bus_voltage
        sumShuntVoltage += shuntVoltage / 1000
        sumCurrent      += shuntVoltage * 10000000
    
    
    print("Bus Voltage:   {} V ".format(sumBusVoltage   / samples ))
    print("Shunt Voltage: {} mV".format(sumShuntVoltage / samples ))
    print("Current:       {} mA".format(sumCurrent      / samples ))


i2c          = busio.I2C(board.SCL, board.SDA)
ina219       = adafruit_ina219.INA219(i2c)

getAverage(ina219, 100, .01)




