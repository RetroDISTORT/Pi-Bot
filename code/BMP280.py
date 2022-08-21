import board
import adafruit_bmp280
i2c = board.I2C()
sensor = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address = 0x76)
sensor.sea_level_pressure = 1013.25

print('Temperature: {} degrees C'.format(sensor.temperature)) 
print('Pressure: {}hPa'.format(sensor.pressure))
print('Altitude: {} meters'.format(sensor.altitude))
