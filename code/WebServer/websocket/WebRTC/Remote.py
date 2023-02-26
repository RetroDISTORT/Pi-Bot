import os               # Required for running command line functions
import time

    
def main():
    #kill_neopixels() # Pixels should auto-shutdownn once the power mosfet is killed automatically
    #kill_display()
    command1 = "/opt/vc/bin/raspivid -t 0 -hf -vf -w 640 -h 480 --nopreview -o - | nc -l 5000" # Fastest
    command2 = "/opt/vc/bin/raspivid -t 0 -w 1280 -h 720 -hf -ih -fps 20 -o - | nc - k -l 5000"
    command3 = "/opt/vc/bin/raspivid -t 0 -hf -vf -w 640 -h 480 --nopreview -o - | cvlv  -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8160}' :demux=h264" # TEST
    
    os.system(command1)
    
if __name__ == "__main__":
    main()
