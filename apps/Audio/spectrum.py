import sys
import wave
import alsaaudio as aa
from struct import unpack
import numpy as np
import scrollphat

wavfile = wave.open(sys.argv[1], 'r')

sample_rate = wavfile.getframerate()
no_channels = wavfile.getnchannels()
chunk = 4096

output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
output.setchannels(no_channels)
output.setrate(sample_rate)
output.setformat(aa.PCM_FORMAT_S16_LE)
output.setperiodsize(chunk)

matrix    = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
power     = []
weighting = [1, 1, 2, 4, 8, 8, 8, 8, 16, 16, 16]

#scrollphat.set_brightness(5)
def power_index(val):
        return int(2 * chunk * val / sample_rate)

def compute_fft(data, chunk, sample_rate):
    global matrix
    data = unpack("%dh" % (len(data) / 2), data)
    data = np.array(data, dtype='h')
    
    fourier = np.fft.rfft(data)
    fourier = np.delete(fourier, len(fourier) - 1)
    
    power = np.abs(fourier)
    matrix[0] = int(np.mean(power[power_index(0)    :power_index(156) :1]))
    matrix[1] = int(np.mean(power[power_index(156)  :power_index(313) :1]))
    matrix[2] = int(np.mean(power[power_index(313)  :power_index(625) :1]))
    matrix[3] = int(np.mean(power[power_index(625)  :power_index(1000) :1]))
    matrix[4] = int(np.mean(power[power_index(1000) :power_index(2000) :1]))
    matrix[5] = int(np.mean(power[power_index(2000) :power_index(3000) :1]))
    matrix[6] = int(np.mean(power[power_index(3000) :power_index(4000) :1]))
    matrix[7] = int(np.mean(power[power_index(4000) :power_index(5000) :1]))
    matrix[8] = int(np.mean(power[power_index(5000) :power_index(6000) :1]))
    matrix[9] = int(np.mean(power[power_index(6000) :power_index(7000) :1]))
    matrix[10] = int(np.mean(power[power_index(7000):power_index(8000) :1]))
    
    matrix = np.divide(np.multiply(matrix, weighting), 1000000)
    matrix = matrix.clip(0, 5)
    matrix = [float(m) for m in matrix]
    
    return matrix

data = wavfile.readframes(chunk)

while data != '':
    output.write(data)
    matrix = compute_fft(data, chunk, sample_rate)
    scrollphat.graph(matrix, 0, 5)
    data = wavfile.readframes(chunk)
