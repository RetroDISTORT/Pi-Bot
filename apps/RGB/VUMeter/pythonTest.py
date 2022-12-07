#cc -fPIC -Wall -Wextra -O2 `pkg-config --cflags libpulse-simple` -shared -pthread -lm `pkg-config --libs libpulse-simple` -o vu.so vu.c
import time
import ctypes

EXIT_SIG = 1

server   = ""
device   = "0"
channels = 2           #    0 <  channels < 32
rate     = 48000       #  128 <   rate    < 250000
updates  = 60          #    1 <  updates  < 200
peak     = "" 
#decay    = 0.95f 
samples  = ctypes.c_size_t(int(rate/updates))

def handler(signum, frame):
    global EXIT_SIG
    EXIT_SIG = 0
    print("Terminating program...", flush=True)

    
def CreateVU(vulib):
    print("Starting VU instance...")
    if vulib.vu_start(server, "vu-bar", device, "VU monitor", channels, rate, samples):
        print(f'Cannot monitor audio source')
        exit()
    print("VU instance created")

def ReadFromVU(vulib):
    new_peak = (ctypes.c_float * channels)()
    if vulib.vu_peak(new_peak, channels) == channels:
        for c in range(channels):
            print(new_peak[c])
    time.sleep(.017)
    
def EndVU(vulib):
    vulib.vu_stop()

    
def main():
    vulib = ctypes.CDLL('./vu.so')
    print("Import Done")

    CreateVU(vulib)

    while EXIT_SIG:
        #new_peak = [0] * channels
        ReadFromVU(vulib)
        
    EndVU(vulib)
    
    
if __name__ == "__main__":
    main()
