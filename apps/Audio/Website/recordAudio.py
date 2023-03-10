from flask import Flask, Response, render_template
import pyaudio

app = Flask(__name__)

FORMAT        = pyaudio.paInt32
CHANNELS      = 2
RATE          = 44100
CHUNK         = 4096 #8192 #4096 #32768 #1024 #512
DEVICE        = 0
bitsPerSample = 32

audioIn       = pyaudio.PyAudio()

def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o

wav_header = genHeader(RATE, bitsPerSample, CHANNELS)


@app.route('/audio')
def audio():
    # start Recording
    def sound():
        wav_header = genHeader(RATE, bitsPerSample, CHANNELS)

        stream  = audioIn.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                               input=True, input_device_index=DEVICE,
                               frames_per_buffer=CHUNK)
        
        print("recording...")
        #frames = []
        first_run = True
        while True:
            if first_run:
                data = wav_header + stream.read(CHUNK)
                first_run = False
            else:
                data = stream.read(CHUNK)
            yield(data)
                
    return Response(sound())
            
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')
            
            
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, threaded=True,port=5000)
