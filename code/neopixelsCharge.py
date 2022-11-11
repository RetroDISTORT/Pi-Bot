import time
import board
import busio
import neopixel
import digitalio
import adafruit_ina219
import os

from rainbowio import colorwheel
from datetime import datetime

def getAverageVoltage(sensor, samples, delay):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    totalVoltage = 0;
    totalShunt   = 0;
    totalCurrent = 0;
    
    for i in range(samples):
        time.sleep(delay)
        newVoltageSample = sensor.bus_voltage
        newShuntSample = sensor.shunt_voltage
        newCurrentSample = sensor.current
        totalVoltage += newVoltageSample
        totalShunt   += newShuntSample
        totalCurrent += newCurrentSample

    voltageAVG = f'{totalVoltage/samples:.3f}'
    shuntAVG   = f'{totalShunt/samples:.6f}'
    currentAVG = f'{totalShunt/samples/.0064:.3f}'  #f'{totalCurrent/samples:.3f}'
    
    print(f'| {voltageAVG}V | {shuntAVG}V | {currentAVG}A | {current_time} |')
    os.system("echo '|" + voltageAVG + " | " + shuntAVG + " | " + currentAVG + " | " + current_time + "|' >> status.txt" )
    return totalVoltage/samples, totalCurrent/samples


def glow(device, delay, red, green, blue):
    device.fill((red, green, 0))
    
    for i in range(100):
        device.brightness = i * .002
        time.sleep(delay)
        device.show()
    for i in range(100, 0,-1):
        device.brightness = i * .002
        time.sleep(delay)
        device.show()
    

def main():
    # enable Neopixels
    SAMPLES = 10
    DELAY   = .2
    VMAX    = 8.42
    VMIN    = 7.40 #6.55 
    
    led = digitalio.DigitalInOut(board.D15)
    led.direction = digitalio.Direction.OUTPUT
    led.value = True

    pixel_pin  = board.D12
    num_pixels = 16
    pixels = neopixel.NeoPixel(pixel_pin, num_pixels)
    ORDER = neopixel.GRB
    pixels = neopixel.NeoPixel( pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER )
    i2c = busio.I2C(board.SCL, board.SDA)
    ina219 = adafruit_ina219.INA219(i2c)

    
    
    print("Current:       {} mA".format(ina219.current))
    while(True):
        VNOW, INOW = getAverageVoltage(ina219, SAMPLES, DELAY)
        CHARGE     = (VNOW - VMIN)*100/(VMAX-VMIN)
        
        pixelGreen = int(CHARGE*2.55) if CHARGE > 0 else 0 
        pixelRed   = 255-pixelGreen   
        pixelBlue  = 0

        #glow(pixels, .01, pixelRed, pixelGreen, pixelBlue)
        
    

if __name__ == "__main__":
    main()
                

