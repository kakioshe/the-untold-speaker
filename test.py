import boto3
import random
import pyaudio
import wave
import time
import os

chunk = 1024
wf = wave.open('1.1.wav', 'rb')
p = pyaudio.PyAudio()

form_1 = pyaudio.paInt16
chans = 2
samp_rate = 44100
chunk = 4096
dev_index = 2

stream = p.open(
    format = form_1,
    channels = chans,
    rate = samp_rate,
    frames_per_buffer = chunk,
    output_device_index = dev_index,
    output = True)
data = wf.readframes(wf.getnframes())

stream.start_stream()
stream.write(data)
time.sleep(0.2)
stream.close()
p.terminate()
