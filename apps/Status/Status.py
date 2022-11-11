import os
import time             # Required for delays
import board            # Required for I2C bus
import busio            # Required for I2C bus
import digitalio        # Required for I2C bus
import adafruit_ina219  # Required for voltage sensor
import adafruit_ssd1306 # Required for OLED displays

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

from PIL import Image, ImageDraw, ImageFont

def get_fonts(dir):
    fontXXL = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 32)
    fontXL  = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 18)
    fontL   = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 16)
    fontM   = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 12)
    fontS   = ImageFont.truetype(dir+"ratchet-clank-psp.ttf", 10)
    fontXS  = ImageFont.truetype(dir+"ratchet-clank-psp.ttf",  8)
    fontXXS = ImageFont.truetype(dir+"3x3-Mono.ttf",  4)
    
    return [fontXXL, fontXL, fontL, fontM, fontS, fontXS, fontXXS]

def get_input():
    if GPIO.input(8) == 0:  # UP
        time.sleep(.1)
        return "UP"
            
    if GPIO.input(25) == 0: # MID
        time.sleep(.1)
        return "SELECT"
            
    if GPIO.input(7) == 0:  # DOWN
        time.sleep(.1)
        return "DOWN"
    
    return "NONE"

def get_from_command(command):
    output = os.popen('vcgencmd measure_temp')
    print(output.read())
    
def get_lipo_status(sensor, samples, delay):
    #now = datetime.now()
    #current_time = now.strftime("%H:%M:%S")
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

    voltageAVG = totalVoltage/samples
    shuntAVG   = totalShunt/samples
    currentAVG = totalShunt/samples/.0110 #only works when charging
    
    #print(f'| {voltageAVG}V | {shuntAVG}V | {currentAVG}A | {current_time} |')
    #os.system("echo '|" + voltageAVG + " | " + shuntAVG + " | " + currentAVG + " | " + current_time + "|' >> status.txt" )
    
    return voltageAVG, shuntAVG, currentAVG

def map_value(value, minimum, maximum):
    maxDif = abs(minimum-maximum) # distance between min and max
    curDif = abs(minimum-value)
    
    return curDif / maxDif * 100

def graph_array(draw, array):
    maxGraph = max(array)
    minGraph = min(array)
    
    for i in range(len(array)-1):
        value1 = 52 - (map_value(array[i]  , minGraph, maxGraph)/2)
        value2 = 52 - (map_value(array[i+1], minGraph, maxGraph)/2)

        draw.line((i+2, value1, i+3, value2), width=0, fill=255) # Voltage Line

    return maxGraph, minGraph

def show_lipo_status(display, fonts, voltage, shunt, current, selected):    
    image  = Image.new('1', (display.width, display.height))
    draw   = ImageDraw.Draw(image)
    
    # Graph
    maxGraph, minGraph = graph_array(draw, voltage)

    # Status
    #draw.text((60 , 0), f'{voltage[-1]:.2f}V' , font=fonts[2], anchor='rm', fill = 255)
    draw.text((60 , 0), f'{maxGraph:.3f}'  , font=fonts[3], anchor='rm', fill = 255)
    draw.text((60 , 50), f'{minGraph:.3f}' , font=fonts[3], anchor='rm', fill = 255)
    
    draw.text((65 , 15), f'V:{voltage[-1]:.3f}V'     , font=fonts[3], anchor='rm', fill = 255)
    draw.text((65 , 25), f'S:{shunt[-1]*1000:.3f}mV' , font=fonts[3], anchor='rm', fill = 255)
    draw.text((65 , 35), f'C:{current[-1]:.3f}A'     , font=fonts[3], anchor='rm', fill = 255)
    draw.text((2 , 51), "Voltage", font=fonts[3], anchor='rm', fill = 255)
                
    display.image(image)
    display.show()

def show_system_status(display, fonts, storage, ram, coretemp, selected):    
    image  = Image.new('1', (display.width, display.height))
    draw   = ImageDraw.Draw(image)
    
    # Graph
    maxGraph, minGraph = graph_array(draw, voltage)

    # Status
    #draw.text((60 , 0), f'{voltage[-1]:.2f}V' , font=fonts[2], anchor='rm', fill = 255)
    draw.text((60 , 0), f'{maxGraph:.3f}'  , font=fonts[3], anchor='rm', fill = 255)
    draw.text((60 , 50), f'{minGraph:.3f}' , font=fonts[3], anchor='rm', fill = 255)
    
    draw.text((65 , 15), f'V:{voltage[-1]:.3f}V'     , font=fonts[3], anchor='rm', fill = 255)
    draw.text((65 , 25), f'S:{shunt[-1]*1000:.3f}mV' , font=fonts[3], anchor='rm', fill = 255)
    draw.text((65 , 35), f'C:{current[-1]:.3f}A'     , font=fonts[3], anchor='rm', fill = 255)
    draw.text((2 , 51), "Voltage", font=fonts[3], anchor='rm', fill = 255)
                
    display.image(image)
    display.show()

def show_wifi_status(display, ssid, strength, ssh, selected):
    quality = [-50, -60, -67, -70, -80, -90] #where < -50 is excellent
    image   = Image.new('1', (display.width, display.height))
    draw    = ImageDraw.Draw(image)
    
    # Graph
    maxGraph, minGraph = graph_array(draw, voltage)

    # Status
    #draw.text((60 , 0), f'{voltage[-1]:.2f}V' , font=fonts[2], anchor='rm', fill = 255)
    draw.text((60 , 0), f'{maxGraph:.3f}'  , font=fonts[3], anchor='rm', fill = 255)
    draw.text((60 , 50), f'{minGraph:.3f}' , font=fonts[3], anchor='rm', fill = 255)
    
    draw.text((65 , 15), f'V:{voltage[-1]:.3f}V'     , font=fonts[3], anchor='rm', fill = 255)
    draw.text((65 , 25), f'S:{shunt[-1]*1000:.3f}mV' , font=fonts[3], anchor='rm', fill = 255)
    draw.text((65 , 35), f'C:{current[-1]:.3f}A'     , font=fonts[3], anchor='rm', fill = 255)
    draw.text((2 , 51), "Voltage", font=fonts[3], anchor='rm', fill = 255)
                
    display.image(image)
    display.show()
    
def main(directory):
    SAMPLES = 1
    DELAY   = .1
    WIDTH   = 128  # DISPLAY
    HEIGHT  = 64   # DISPLAY
    BORDER  = 5    # DISPLAY
    
    voltageHist = [0] * 50
    currentHist = [0] * 50
    shuntHist    = [0] * 50
    selected = 0
        
    i2c = busio.I2C(board.SCL, board.SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    ina219 = adafruit_ina219.INA219(i2c)

    fontList = get_fonts('/opt/boobot/fonts/')
    
    oled.contrast(1) # Max contrast is 255
    
    GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # DOWN       Order:
    GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # UP      [U][C][D][O]
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP) # CENTER

    input = ""
    
    while(input != "SELECT"):
        voltage, shunt, current = get_lipo_status(ina219, SAMPLES, DELAY)
        
        voltageHist.append(voltage)
        currentHist.append(current)
        shuntHist.append(shunt)
        
        voltageHist.pop(0)
        currentHist.pop(0)
        shuntHist.pop(0)

        show_lipo_status(oled, fontList, voltageHist, shuntHist, currentHist, selected)
        input = get_input()

    
if __name__ == "__main__":
    main('/opt/boobot/')    
