import board
import busio
import adafruit_ssd1306
import digitalio
from PIL import Image, ImageDraw, ImageFont

print("Kill Screen")

WIDTH = 128
HEIGHT = 64
BORDER = 0

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)

oled.fill(0)

oled.show()
