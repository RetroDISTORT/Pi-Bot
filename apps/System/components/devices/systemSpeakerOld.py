# Using pyaudio for mic and speaker is an issue
# Both block eachother
# Keeping this here just in case

from av import AudioFrame
import pyaudio
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
        self.sample_rate     = 44100#44100#48000 #8000
        self.samples         = 960#int(self.audio_ptime * self.sample_rate)
        self.sample_format   = pyaudio.paInt16 #s16
        self.sample_layout   = "stereo"
        self.sample_channels = 2
        self.sample_codec    = "pcm_s16le"
        self.INDEX           = 0
        self.chunk           = int(self.audio_ptime*self.sample_rate)*15
        self.__track         = {}
        self.task            = None
        
        self.audio_player    = pyaudio.PyAudio()
        self.stream_player   = self.audio_player.open(format=self.sample_format,
                                                      channels=self.sample_channels,
                                                      rate=self.sample_rate,
                                                      output=True,
                                                      input=False,
                                                      output_device_index = self.INDEX,
                                                      frames_per_buffer = self.chunk
                                                      )


    def addTrack(self, track):
        self.__track=track
        pass
        #if track.kind == "audio":
            #self.__container.add_stream(self.sample_codec)
            
        #self.__track[track] = MediaRecorderContext(stream)


    async def start(self): #Start Playing
        #for track, context in self.__track.items():
        #    if context.task is None:
                self.task = asyncio.ensure_future(self.__run_track(self.__track))
        


    async def stop(self): #Stop Playing
        self.__track = {}
        
        
    async def __run_track(self, track: MediaStreamTrack):
        #print("running")
        while True:
            try:
                #print("waiting")
                frame = await track.recv()
                #print(frame, len(frame.to_ndarray()[0]) )
                frame_data = frame.to_ndarray()[0]
                #print(frame)
                self.stream_player.write(frame_data, self.samples)
            except MediaStreamError:
                print("error track.recv")
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
