import board
import busio
import adafruit_ssd1306
import digitalio
from PIL import Image, ImageDraw, ImageFont

import socket


hostname=socket.gethostname()
IPAddr=socket.gethostbyname(hostname)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
print("Your Computer Name is:"+hostname)
print("Your Computer IP Address is:"+IPAddr)
print("ssh: retro@"+(s.getsockname()[0]))

WIDTH = 128
HEIGHT = 64
BORDER = 5

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
font = ImageFont.load_default()
text = "> retro@"+(s.getsockname()[0])

image = Image.new('1', (oled.width, oled.height))
draw = ImageDraw.Draw(image)
(font_width, font_height) = font.getsize(text)


oled.fill(0)

(font_width, font_height) = font.getsize(text)
draw.text((oled.width//2 - font_width//2, oled.height//2 - font_height//2), text, font=font, fill=255)
oled.image(image)

oled.show()
