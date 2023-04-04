from av import AudioFrame
import av
import numpy as np
import sounddevice as sd

from threading import Thread, Event, Lock
from aiortc.mediastreams import MediaStreamTrack


class SystemMic(MediaStreamTrack):
    kind = "audio"
    
    def __init__(self):
        super().__init__()
        
        self.kind         = "audio"
        self.RATE         = 44100
        self.AUDIO_PTIME  = 0.020                                    # 20ms audio packetization
        self.SAMPLES      = int(self.AUDIO_PTIME * self.RATE)
        self.FORMAT       = 'int32' #pyaudio.paInt32
        self.CHANNELS     = 2
        self.CHUNK        = int(self.RATE*self.AUDIO_PTIME)*10
        self.DEVICE       = 0
        self.FORMATAF     = 's16'   #'s32'                           # s32_le
        self.LAYOUT       = 'stereo'
        self.sampleCount  = 0
        self.micData      = []
        self.capturedData = []
        self.live         = 1

        self.stream = sd.InputStream(samplerate = self.RATE, blocksize = self.CHUNK, device = self.DEVICE,
                                     channels = self.CHANNELS, dtype = self.FORMAT, callback = self.callback)

        #thread
        self.micData          = None
        self.micDataLock      = Lock()
        self.newMicDataEvent  = Event()
        self.newMicDataEvent.clear()
        self.captureThread    = Thread(target=self.capture)
        self.captureThread.start()


    def capture(self):
        with self.stream:
            while self.live:
                if len(self.capturedData)!=0:
                    with self.micDataLock:
                        #print("lock")
                        #print(len(self.capturedData))
                        self.micData = np.array(self.capturedData).flatten()
                        self.capturedData = []
                        #print(len(self.capturedData))
                        print('.')
                        self.newMicDataEvent.set()
            return
                
            
        
    def callback(self, indata, outdata, frames, time):#, status):
        self.capturedData = indata
    
        
    async def recv(self):
        newMicData = None
            
        self.newMicDataEvent.wait()

        with self.micDataLock:
            print("-")
            data  = self.micData
            #print(data)
            data  = (data/2).astype('int32')
            data  = np.array([(data>>16).astype('int16')])
            self.newMicDataEvent.clear()
        
        frame   = av.AudioFrame.from_ndarray(data, self.FORMATAF, layout=self.LAYOUT)
        frame.pts         = self.sampleCount
        frame.rate        = self.RATE
        self.sampleCount += frame.samples

        #self.stream.write(frame) # Fill it with silence
        #print(newMicData)
        #print(frame.pts)
        #frame.samples = self.SAMPLES
        #print(mic_data)
        #print(frame)
        #print(forceStop)
        #<av.AudioFrame 0, pts=0, 960 samples at 48000Hz, stereo, s16 at 0x6c1660b0>
        #<av.AudioFrame 0, pts=960, 960 samples at 48000Hz, stereo, s16 at 0x6c1660f0>
        return frame
            
    def stop(self):
        self.live = 0
        super.stop()
