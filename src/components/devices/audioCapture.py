import pasimple

class AudioCapture:
    def __init__(self):
        self.audioServer    = ""
        self.audioDevice    = "0" 
        self.audioChannels  = 2                    #    0 <  channels < 32
        self.audioRate      = 48000                #  128 <   rate    < 250000
        self.audioUpdates   = 30                   #    1 <  updates  < 200
        self.audioSamples   = int(audioRate/audioUpdates)*2#2048                 # ctypes.c_size_t(int(rate/updates))
        self.audioDirection = pasimple.PA_STREAM_RECORD
        self.audioFormat    = pasimple.PA_SAMPLE_S16LE
        self.audioAppName   = 'pythonVU'
        self.audioStream    = None
        self.audioServer    = None
        self.audioCapture   = pasimple.PaSimple(self.audioDirection, self.audioFormat, self.audioChannels, self.audioRate, app_name=self.audioAppName, stream_name=self.audioStream, server_name=self.audioServer, device_name=self.audioDevice)

        
    def __del__(self):
        self.audioCapture.close()
    
