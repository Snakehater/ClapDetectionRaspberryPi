class GetClap():
    checkLength = 0
    def __init__(self):
        import wave
        import struct
        smallChunk = 6
        bigChunk = 20
        startTrigger = 0.2
        middleTrigger = 0.5
        middleJump = 100
        endTrigger = 0.4 # percentage
        endJump = 2300
        self.checkLength = middleJump+endJump+bigChunk

    def parseToFloat(self, numFrames, channels, frames):
        import struct
        numFrames /= 2
        frames = b''.join(frames)
        a = struct.unpack("%ih" % (numFrames* channels), frames)
        a = [float(val) / pow(2, 15) for val in a]
        return a
    def checkClap(self, numFrames, channels, frames):
        import wave
        import struct
        waveArr = self.parseToFloat(numFrames, channels, frames)

        smallChunk = 6
        bigChunk = 20
        startTrigger = 0.2
        middleTrigger = 0.5
        middleJump = 100
        endTrigger = 0.4 # percentage
        endJump = 2300

        clap = False

        for idx in range(len(waveArr)):
            if idx+middleJump+endJump+bigChunk > len(waveArr):
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
        if clap is False:
            #print("""it's not a clap""")
            return False
    def checkClapFile(self, fileName):
        import wave
        import struct
        waveArr = self.wav_to_floats(fileName)

        smallChunk = 6
        bigChunk = 20
        startTrigger = 0.2
        middleTrigger = 0.5
        middleJump = 100
        endTrigger = 0.4 # percentage
        endJump = 2300

        clap = False

        for idx in range(len(waveArr)):
            if idx+middleJump+endJump+bigChunk > len(waveArr):
                break

            f = abs(waveArr[idx])

            average = 0.0
            for i in range(smallChunk):
                average += abs(waveArr[idx+i])
            average /= smallChunk
            if average > startTrigger:
                print('start ' + str(average))
                average = 0.0
                for i in range(idx+middleJump, idx+middleJump+bigChunk):
                    average += abs(waveArr[i])
                average /= bigChunk
                if average > middleTrigger:
                    print('middle ' + str(average))
                    averagePeak = average
                    average = 0.0
                    for i in range(idx+middleJump+endJump, idx+middleJump+endJump+bigChunk):
                        average += abs(waveArr[i])
                    average /= bigChunk
                    if average < averagePeak*endTrigger:
                        print('end ' + str(average))
                        print("""it's a clap""")
                        clap = True
                        return True
                        break
        if clap is False:
            print("""it's not a clap""")
            return False
    def wav_to_floats(self, wave_file):
        import wave
        import struct
        w = wave.open(wave_file)
        astr = w.readframes(w.getnframes())
        # convert binary chunks to short
        a = struct.unpack("%ih" % (w.getnframes()* w.getnchannels()), astr)
        a = [float(val) / pow(2, 15) for val in a]
        return a
# GetClap().checkClap('testfirst.wav')
