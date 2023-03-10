from av import AudioFrame
import pyaudio
import av
import numpy as np

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
        self.FORMAT       = pyaudio.paInt32
        self.CHANNELS     = 2
        self.CHUNK        = int(self.RATE*self.AUDIO_PTIME)
        self.INDEX        = 0
        self.FORMATAF     = 's16'   #'s32'                           # s32_le
        self.LAYOUT       = 'stereo'
        self.sampleCount  = 0

        self.audio        = pyaudio.PyAudio()
        self.stream       = self.audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE,
                                            input=True, input_device_index=self.INDEX,
                                            frames_per_buffer=self.CHUNK)
        #thread
        self.micData          = None
        self.micDataLock      = Lock()
        self.newMicDataEvent  = Event()
        self.newMicDataEvent.clear()
        self.captureThread    = Thread(target=self.capture)
        self.captureThread.start()
        

    def capture(self):
        while True:
            data  = np.fromstring(self.stream.read(self.CHUNK),dtype=np.int32)
            
            with self.micDataLock:
                self.micData = data
                self.newMicDataEvent.set()
    
        
    async def recv(self):
        newMicData = None
            
        self.newMicDataEvent.wait()

        with self.micDataLock:
            data  = self.micData
            data  = (data/2).astype('int32')
            data  = np.array([(data>>16).astype('int16')])
            self.newMicDataEvent.clear()
        
        frame   = av.AudioFrame.from_ndarray(data, self.FORMATAF, layout=self.LAYOUT)
        frame.pts         = self.sampleCount
        frame.rate        = self.RATE
        self.sampleCount += frame.samples

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
        super.stop()
        self.captureThread.kill()
