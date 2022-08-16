import board
import busio
import adafruit_ina219
i2c = busio.I2C(board.SCL, board.SDA)
ina219 = adafruit_ina219.INA219(i2c)
print("Bus Voltage:   {} V".format(ina219.bus_voltage))
print("Shunt Voltage: {} mV".format(ina219.shunt_voltage / 1000))
print("Current:       {} mA".format(ina219.current))
