import pyaudio
import wave
import numpy as np

FORMAT = pyaudio.paInt32
CHANNELS = 2
RATE = 44100
CHUNK = 4096
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"
device_index = 0
audio = pyaudio.PyAudio()

FORMAT_OUT = pyaudio.paInt16

print("----------------------record device list---------------------")
info = audio.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
    if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))

print("-------------------------------------------------------------")

index = 0#int(input())
print("recording via index "+str(index))

stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,input_device_index = index,
                    frames_per_buffer=CHUNK)
print ("recording started")
Recordframes = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    #data = stream.read(CHUNK)
    
    data = np.fromstring(stream.read(CHUNK),dtype=np.int32)
    print(data)
    
    data = (data/2).astype('int32')
    data = (data>>16).astype('int16')
    print(data)
    
    Recordframes.append(data)
print ("recording stopped")

stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT_OUT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(Recordframes))
waveFile.close()
