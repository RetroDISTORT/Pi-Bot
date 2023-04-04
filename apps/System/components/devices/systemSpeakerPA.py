from av import AudioFrame
import sounddevice as sd
import av
import numpy as np
import asyncio

#import sounddevice as sd
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription


class MediaStreamError(Exception):
    pass


class MediaRecorderContext:
    def __init__(self, stream):
        self.started = False
        self.stream = stream
        self.task = None


class SystemSpeaker():        
    def __init__(self):
        self.audio_ptime     = 0.020 # 20ms audio packetization
        self.sample_rate     = 48000#44100#48000 #8000
        self.samples         = 960#int(self.audio_ptime * self.sample_rate)
        #self.sample_format   = pyaudio.paInt16 #s16
        self.sample_layout   = "stereo"
        self.sample_channels = 2
        self.sample_codec    = "pcm_s16le"
        self.chunk           = int(self.audio_ptime*self.sample_rate)*15
        self.__track         = {}
        
        sd.default.device     = 0
        sd.default.channels   = self.sample_channels
        sd.default.latency    = 'high'
        sd.default.samplerate = self.sample_rate
        sd.default.dtype      = 'int16'

        # self.audio_player    = pyaudio.PyAudio()
        # self.audio_player.open(format=self.sample_format,
        #                        channels=self.sample_channels,
        #                        rate=self.sample_rate,
        #                        output=True,
        #                        frames_per_buffer = self.chunk
        #                        )


    def addTrack(self, track):
        self.__track=track
        pass
        #if track.kind == "audio":
            #self.__container.add_stream(self.sample_codec)
            
        #self.__track[track] = MediaRecorderContext(stream)


    async def start(self): #Start Playing
        print("start")
        #for track, context in self.__track.items():
        #    if context.task is None:
        #        context.task =
        asyncio.ensure_future(self.__run_track(self.__track))
        


    async def stop(self): #Stop Playing
        self.__track = {}
        
        
    async def __run_track(self, track: MediaStreamTrack):
        print("running")
        while True:
            try:
                #print("waiting")
                frame = await track.recv()
            except MediaStreamError:
                return
            
            #print(frame, len(frame.to_ndarray()[0]) )
            #frame_data = frame.to_ndarray()[0]
            audio = frame.to_ndarray()[0]

            #print(audio.reshape(-1, 1))
            
            #l = np.vstack(audio[0::2])
            #r = np.vstack(audio[1::2])
            #frame_data = np.hstack((l,r))

            frame_data = np.zeros(960*10)#audio[0::2]
            #print(l)
            #print(r)
            print(frame_data)
            
            #print(frame_data.shape[0])
            sd.play(frame_data, mapping=1, samplerate=48000 )
            
            #self.stream_player.write(frame_data, self.samples)
            #free = self.stream_player.get_write_available()
            #print(free)
            #if free > CHUNK: # Is there a lot of space in the buffer?
            #    tofill = free - CHUNK
            #    stream.write(SILENCE * tofill) # Fill it with silence
           
        #if not context.started:
        #    context.started = True
            
        

        #print()
        
        #for packet in context.stream.encode(frame):
        #    self.__container.mux(packet)
