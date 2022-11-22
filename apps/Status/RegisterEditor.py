import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)

def find(deviceAddress):
    return deviceAddress in i2c.scan()

def scan():
    return [hex(a) for a in i2c.scan()]

def readFrom(deviceAddress, register, registerSize = 2):
    bytesRead = bytearray(registerSize)
    
    i2c.writeto(deviceAddress, bytes([register]))
    i2c.readfrom_into(deviceAddress, bytesRead)
    
    return [hex(b) for b in bytesRead]

def writeTo(deviceAddress, register, value, registerSize = 2):
    bytesRead = bytearray(registerSize)

    
    i2c.writeto(deviceAddress, bytes([register, value]))
    #i2c.readfrom_into(deviceAddress, bytesRead)
    
    #return [hex(b) for b in bytesRead]

def main():
    print(scan())
    #print(find(0x3C))
    #print(readFrom(0x3C, 0xff))
    writeTo(0x3C, 0xff, 0x00)
    print(readFrom(0x3C, 0xff))
    

if __name__ == "__main__":
    main()
