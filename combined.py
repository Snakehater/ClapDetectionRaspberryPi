import pyaudio
import wave
import struct
from time import sleep
import threading
import requests

def toggleLights():
   #print('toggle lights')
    try:
            requests.get('https://elvigo.com/vigor/servers/lightscontrol/togglelights.php')
    except Exception as e:
            print("Internet connection not established")
            print(e)
           #print('\n\n\n')

smallChunk = 6
bigChunk = 20
startTrigger = 0.2
middleTrigger = 0.4
middleJump = 100
middleJumpTime = 0.003
endTrigger = 0.4 # percentage
endJump = 2300
endJumpTime = 0.085
checkLength = middleJump+endJump+bigChunk

#pa = pyaudio.PyAudio()
#for x in range(0,pa.get_device_count()):
#      #print(pa.get_device_info_by_index(x))

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 48000 # 44.1kHz sampling rate
chunk = 8192 # 2^12 samples for buffer is default, now set to 2^13 as the sampling rate is higher than normal
record_secs = 1 # seconds to record
dev_index = 2 # device index found by p.get_device_info_by_index(ii)
# wav_output_filename = 'test1.wav' # name of .wav file

audio = pyaudio.PyAudio() # create pyaudio instantiation

print('####################################################\n\n\n\n')
for x in range(0,audio.get_device_count()):
   print(audio.get_device_info_by_index(x))
print('\n\n\n\n####################################################')

# create pyaudio stream
stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)

stream.stop_stream()
stream.close()

# stream10 = audio.open(format = form_1,rate = samp_rate,channels = chans, \
#                     input_device_index = dev_index,input = True, \
#                     frames_per_buffer=10)
streambigchunk = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=bigChunk)
print("recording")
# frames = []
# numFrames = 0
# limit = Clap().checkLength*4
#
# loop through stream and append audio chunks to frame array
# for ii in range(0,int((samp_rate/chunk)*record_secs)):
#     data = stream.read(chunk)
#     frames.append(data)
#     numFrames += len(data)
#
##print("finished recording")
def uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        return uptime_seconds
def parseToFloat(numFrames, channels, framesIn):
    frames = b''.join(framesIn)
    a = struct.unpack("%ih" % (numFrames* channels), frames)
    a = [float(val) / pow(2, 15) for val in a]
    return a
def checkClap(frames):
    ##print(frames)
    average = 0
    for f in frames:
        average += abs(f)
    #print(average/len(frames))
    if average/len(frames) > startTrigger:
       #print('\n\nstart: ' + str(average/len(frames)))
        sleep(middleJumpTime)
        frames = []
        data = streambigchunk.read(bigChunk, exception_on_overflow = False)
        frames.append(data)
        frames = parseToFloat(bigChunk, chans, frames)
        average = 0
        for f in frames:
            average += abs(f)
       #print(average/len(frames))
        if average/len(frames) > middleTrigger:
           #print('peak: ' + str(average/len(frames)))
            averagePeak = average
            sleep(endJumpTime)
            frames = []
            data = streambigchunk.read(bigChunk, exception_on_overflow = False)
            frames.append(data)
            frames = parseToFloat(bigChunk, chans, frames)
            average = 0
            for f in frames:
                average += abs(f)
           #print(average/len(frames))
            if average < averagePeak*endTrigger:
               #print("""it's a clap""")
               #print('end: ' + str(average/len(frames)))
                return True

    return False

isDoubleClap = False

def checkClapEntireArrLambda(startIdx, steps, waveArr):
    global isDoubleClap
    global smallChunk
    global bigChunk
    global startTrigger
    global middleTrigger
    global middleJump
    global middleJumpTime
    global endTrigger
    global endJump
    global endJumpTime
    global checkLength

    clap = False

    for idx in range(startIdx, len(waveArr), steps):
        ##print(idx)
        if idx+middleJump+endJump+bigChunk > len(waveArr) or isDoubleClap is True:
            break

        f = abs(waveArr[idx])

        average = 0.0
        for i in range(smallChunk):
            average += abs(waveArr[idx+i])
        average /= smallChunk
        if average > startTrigger:
            #print('start ' + str(average))
            average = 0.0
            for i in range(idx+middleJump, idx+middleJump+bigChunk):
                average += abs(waveArr[i])
            average /= bigChunk
            if average > middleTrigger:
                #print('middle ' + str(average))
                averagePeak = average
                average = 0.0
                for i in range(idx+middleJump+endJump, idx+middleJump+endJump+bigChunk):
                    average += abs(waveArr[i])
                average /= bigChunk
                if average < averagePeak*endTrigger:
                    #print('end ' + str(average))
                   #print("""it's a clap""")
                    clap = True
                    break
                    isDoubleClap = True

def checkClapEntireArr(numFrames, channels, frames):
    global isDoubleClap
    waveArr = parseToFloat(numFrames, channels, frames)

    global smallChunk
    global bigChunk
    global startTrigger
    global middleTrigger
    global middleJump
    global middleJumpTime
    global endTrigger
    global endJump
    global endJumpTime
    global checkLength

    clap = False

    threading.Thread(target=(lambda: checkClapEntireArrLambda(1, 4, waveArr))).start()
    threading.Thread(target=(lambda: checkClapEntireArrLambda(2, 4, waveArr))).start()
    threading.Thread(target=(lambda: checkClapEntireArrLambda(3, 4, waveArr))).start()

    for idx in range(0, len(waveArr), 4):
        ##print(idx)
        if idx+middleJump+endJump+bigChunk > len(waveArr) or isDoubleClap is True:
            break

        f = abs(waveArr[idx])

        average = 0.0
        for i in range(smallChunk):
            average += abs(waveArr[idx+i])
        average /= smallChunk
        if average > startTrigger:
            #print('start ' + str(average))
            average = 0.0
            for i in range(idx+middleJump, idx+middleJump+bigChunk):
                average += abs(waveArr[i])
            average /= bigChunk
            if average > middleTrigger:
                #print('middle ' + str(average))
                averagePeak = average
                average = 0.0
                for i in range(idx+middleJump+endJump, idx+middleJump+endJump+bigChunk):
                    average += abs(waveArr[i])
                average /= bigChunk
                if average < averagePeak*endTrigger:
                    #print('end ' + str(average))
                    print("""it's a clap""")
                    clap = True
                    return True
                    break
    if isDoubleClap is True:
        return True
        isDoubleClap = False
    if clap is False:
        #print("""it's not a clap""")
        return False

def checkDoubleClap(frames):
    global streambigchunk
    ##print(frames)
    average = 0
    for f in frames:
        average += abs(f)
    ##print(average/len(frames))
    if average/len(frames) > startTrigger:
       #print('\n\nstart: ' + str(average/len(frames)))
        sleep(middleJumpTime)
        frames = []
        data = streambigchunk.read(bigChunk, exception_on_overflow = False)
        frames.append(data)
        frames = parseToFloat(bigChunk, chans, frames)
        average = 0
        for f in frames:
            average += abs(f)
       #print(average/len(frames))
        if average/len(frames) > middleTrigger:
           #print('peak: ' + str(average/len(frames)))
            averagePeak = average
            sleep(endJumpTime)
            frames = []
            data = streambigchunk.read(bigChunk, exception_on_overflow = False)
            frames.append(data)
            frames = parseToFloat(bigChunk, chans, frames)
            average = 0
            for f in frames:
                average += abs(f)
           #print(average/len(frames))
            if average < averagePeak*endTrigger:
                print("""it's a clap""")
               #print('end: ' + str(average/len(frames)))

                streambigchunk.stop_stream()
                streambigchunk.close()

                # stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                #                     input_device_index = dev_index,input = True, \
                #                     frames_per_buffer=chunk)
                #
                # frames = []
                # numFrames = 0
                #
                # #loop through stream and append audio chunks to frame array
                print("searching for next clap")
                # for ii in range(0,int((samp_rate/chunk)*record_secs)):
                #     data = stream.read(chunk)
                #     frames.append(data)
                #     numFrames += len(data)
                #
                # stream.stop_stream()
                # stream.close()
                #
                # numFrames /= 2

                # return checkClapEntireArr(numFrames, chans, frames)
                for ii in range(0, 50):
                    frames = []
                    streambigchunk.stop_stream()
                    streambigchunk.close()
                    streambigchunk = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                                        input_device_index = dev_index,input = True, \
                                        frames_per_buffer=bigChunk)
                    data = streambigchunk.read(bigChunk, exception_on_overflow = True)
                    frames.append(data)
                    frames = parseToFloat(bigChunk, chans, frames)
                    # threading.Thread(target=(lambda: checkClap(frames))).start()
                    if checkClap(frames):
                        return True
                        break
                print('end')

    return False

# run forever

while True:
    frames = []
    streambigchunk.stop_stream()
    streambigchunk.close()
    streambigchunk = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=bigChunk)
    data = streambigchunk.read(bigChunk, exception_on_overflow = True)
    frames.append(data)
    frames = parseToFloat(bigChunk, chans, frames)
    # threading.Thread(target=(lambda: checkClap(frames))).start()
    if checkDoubleClap(frames):
        toggleLights()


# stop the stream, close it, and terminate the pyaudio instantiation
streambigchunk.stop_stream()
streambigchunk.close()
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
#        #print('\n\n\n\n This is a clap')
# else:
#        #print('\n\n\n\n This is not a clap')
