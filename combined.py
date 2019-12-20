import pyaudio
import wave
import struct
from time import sleep

class Clap():
    checkLength = 0
    def __init__(self):
        self.smallChunk = 6
        self.bigChunk = 20
        self.startTrigger = 0.2
        self.middleTrigger = 0.5
        self.middleJump = 100
        self.middleJumpTime = 0.003
        self.endTrigger = 0.4 # percentage
        self.endJump = 2300
        self.endJumpTime = 0.045
        self.checkLength = self.middleJump+self.endJump+self.bigChunk

#pa = pyaudio.PyAudio()
#for x in range(0,pa.get_device_count()):
#       print(pa.get_device_info_by_index(x))

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 48000 # 44.1kHz sampling rate
chunk = 8192 # 2^12 samples for buffer is default, now set to 2^13 as the sampling rate is higher than normal
record_secs = 3 # seconds to record
dev_index = 2 # device index found by p.get_device_info_by_index(ii)
wav_output_filename = 'test1.wav' # name of .wav file

audio = pyaudio.PyAudio() # create pyaudio instantiation

# create pyaudio stream
stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
print("recording")
# frames = []
# numFrames = 0
# limit = Clap().checkLength*4

# loop through stream and append audio chunks to frame array
# for ii in range(0,int((samp_rate/chunk)*record_secs)):
#     data = stream.read(chunk)
#     frames.append(data)
#     numFrames += len(data)
#
# print("finished recording")

def parseToFloat(numFrames, channels, framesIn):
    frames = b''.join(framesIn)
    a = struct.unpack("%ih" % (numFrames* channels), frames)
    a = [float(val) / pow(2, 15) for val in a]
    return a

# run forever

smallChunk = Clap().smallChunk
bigChunk = Clap().bigChunk
startTrigger = Clap().startTrigger
middleTrigger = Clap().middleTrigger
middleJump = Clap().middleJump
middleJumpTime = Clap().middleJumpTime
endTrigger = Clap().endTrigger # percentage
endJump = Clap().endJump
endJumpTime = Clap().endJumpTime
checkLength = middleJump+endJump+bigChunk

while True:
    frames = []
    data = stream.read(smallChunk, exception_on_overflow = False)
    frames.append(data)
    frames = parseToFloat(smallChunk, chans, frames)
    average = 0
    for f in frames:
        average += abs(f)
    if average/len(frames) > startTrigger:
        sleep(middleJumpTime)
        frames = []
        data = stream.read(smallChunk, exception_on_overflow = False)
        frames.append(data)
        frames = parseToFloat(smallChunk, chans, frames)
        average = 0
        for f in frames:
            average += abs(f)

# stop the stream, close it, and terminate the pyaudio instantiation
stream.stop_stream()
stream.close()
audio.terminate()

#print(str(frames[0]))

#framesArr = str(frames[0]).split("""\\x""")
#outStr = ''
#for h in framesArr:
#       outStr += str(int(h, 16))
#print(outStr)

# save the audio frames as .wav file
#wavefile = wave.open(wav_output_filename,'wb')
#wavefile.setnchannels(chans)
#wavefile.setsampwidth(audio.get_sample_size(form_1))
#wavefile.setframerate(samp_rate)
#wavefile.writeframes(b''.join(frames))
#wavefile.close()
#
# if GetClap().checkClap(numFrames, chans, frames):
#         print('\n\n\n\n This is a clap')
# else:
#         print('\n\n\n\n This is not a clap')
