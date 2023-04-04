# Using pyaudio for mic and speaker is an issue
# Both block eachother
# Keeping this here just in case

from av import AudioFrame
import pyaudio
import av
import numpy as np
import asyncio

from threading import Thread, Event, Lock
from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription


class MediaStreamError(Exception):
    pass


class MediaRecorderContext:
    def __init__(self, stream):
        self.started = False
        self.stream = stream
        self.TASK = None


class SystemSpeaker():        
    def __init__(self):
        self.PTIME           = 0.020 # 20ms audio packetization
        self.RATE            = 44100 #44100#48000 #8000
        self.SAMPLES         = 960 #int(self.audio_ptime * self.sample_rate)
        self.FORMAT          = pyaudio.paInt16 #s16
        self.CHANNELS        = 2
        self.INDEX           = 0
        self.CHUNK           = int(self.PTIME*self.RATE)*15
        self.TRACK           = {}
        self.TASK            = None
        self.LIVE            = True
        self.DATA            = None
        
        self.audio_player    = pyaudio.PyAudio()
        self.stream_player   = self.audio_player.open(format              = self.FORMAT,
                                                      channels            = self.CHANNELS,
                                                      rate                = self.RATE,
                                                      output              = True,
                                                      input               = False,
                                                      output_device_index = self.INDEX,
                                                      frames_per_buffer   = self.CHUNK
                                                      )
        #thread
        self.dataLock      = Lock()
        self.newDataEvent     = Event()
        self.newDataEvent.clear()
        self.playThread    = Thread(target=self.play)
        self.playThread.start()

        
    def play(self):
        while self.LIVE:
            self.newDataEvent.wait()
            with self.dataLock:
                frame_data = self.DATA.to_ndarray()[0]
            self.stream_player.write(frame_data, self.SAMPLES)
                
        
    def addTrack(self, track):
        self.TRACK=track
        pass


    async def start(self): #Start Playing
        print("start")
        self.TASK = asyncio.ensure_future(self.__run_track(self.TRACK))
        
        
    async def __run_track(self, track: MediaStreamTrack):
        while self.LIVE:
            try:
                frame = await track.recv()
                
                with self.dataLock:
                    self.DATA = frame
                    self.newDataEvent.set()
                    self.newDataEvent.clear()
                    
            except MediaStreamError:
                print("error track.recv")

            
    async def stop(self): #Stop Playing
        self.LIVE  = False
        self.TRACK = {}
